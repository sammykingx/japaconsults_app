from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import extract, func
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_crud, db_models, schema
from datetime import date, datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr
import calendar, time


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
    responses={
        200: {"description": "Successful response"},
        400: {"description": "Missing required data to process request"},
        401: {"description": "Unauthorized access to resource"},
        403: {"description": "Cannot access resource"},
        404: {"description": "Resource Not Found"},
        500: {"description": "Internal server error"},
    },
)


class PendingPayments(BaseModel):
    ref_id: str
    rave_txRef: str
    invoice_id: str
    paid: bool = False
    payer_email: EmailStr | str


class PaymentResponse(PendingPayments, BaseModel):
    # ref_id: str
    # rave_txRef: str
    # invoice_id: str
    paid_by: str | None
    amount: float
    # paid: bool
    paid_at: datetime | None
    # payer_email: EmailStr | str
    payment_type: str


@router.get(
    "/all",
    summary="returns all payments record",
    description="Returns all payment records on the platform. Can be used by "
    "all users irrespective of their roles, the results is been filtered "
    "internally based on the role type of the active user",
    response_model=list[PaymentResponse],
)
async def app_payments(
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """get all payments records"""

    if active_user["role"] == "user":
        records = db_crud.filter_record_in_lifo(
            db,
            db_models.Payments,
            db_models.Payments.paid_at,
            payer_email=active_user["email"],
        )

    else:
        records = db_crud.all_record_in_lifo(
            db, db_models.Payments, db_models.Payments.paid_at
        )

    # if not records:
    #    raise HTTPException(
    #        status_code=status.HTTP_404_NOT_FOUND,
    #        detail="No payment record found",
    #    )

    check_record(records)

    return [payments_serializer(record) for record in records]


@router.get(
    "/pending",
    summary="To see all pending payments on the system",
    description="Use this endpoints to see all pending payments on the "
    "system, can be used by all user roles.",
    response_model=list[PendingPayments],
)
async def pending_payments(
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """return all pending payments"""

    if active_user["role"] == "user":
        records = db_crud.filter_record_in_lifo(
            db,
            db_models.Payments,
            db_models.Payments.ref_id,
            paid=False,
            payer_email=active_user["email"],
        )

    else:
        records = db_crud.filter_record_in_lifo(
            db, db_models.Payments, db_models.Payments.ref_id, paid=False
        )

    check_record(records)
    return [payments_serializer(record) for record in records]


@router.get(
    "/totalRevenue",
    summary="Returns the total revenue on the system",
    description="Returns the total revenue generated based on month"
    "should be used by previledged users",
)
async def total_revenue(
    year: int,
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
    month: int | None = None,
):
    """returns the total revenue"""

    if active_user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unathorized access to resource",
        )

    if month:
        if month <= 0 or month > 12:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="month should be within 1 to 12",
            )

        else:
            records = (
                db.query(db_models.Invoices)
                .filter(
                    extract("month", db_models.Invoices.paid_at) == month,
                    extract("year", db_models.Invoices.paid_at) == year,
                )
                .all()
            )

    else:
        records = (
            db.query(
                func.extract("year", db_models.Invoices.paid_at).label(
                    "year"
                ),
                func.extract("month", db_models.Invoices.paid_at).label(
                    "month"
                ),
                func.sum(db_models.Invoices.price).label("amount"),
            )
            .group_by("year", "month")
            .all()
        )

        build_yearly_report(records)

    print(records)

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint still in development",
    )


@router.get(
    "/totalSpend",
    summary="Returns the total amount spent by a user",
    description="Returns the total amount spent by a user on the platform. "
    "should not be used by previledged users",
)
async def user_total_spend(
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """Returns the total amount spent by a user"""

    if active_user["role"] != "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unathorized access to resource",
        )

    spent_amount = 0.0
    records = db_crud.get_by(
        db, db_models.Invoices, to_email=active_user["email"], paid=True
    )

    if not records:
        return {"user": active_user, "total_spend": spent_amount}

    else:
        spent_amount = sum(
            record.price for record in records if record.paid
        )

    return {"user": active_user, "total_spend": spent_amount}


def check_record(records):
    """checks if the record is empty"""

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No payment record found",
        )


def payments_serializer(record):
    """serializes the payments records"""

    return {
        "ref_id": record.ref_id,
        "rave_txRef": record.flw_txRef,
        "invoice_id": record.inv_id,
        "paid_by": record.paid_by,
        "amount": record.amount,
        "paid": record.paid,
        "paid_at": record.paid_at,
        "payer_email": record.payer_email,
        "payment_type": record.payment_type,
    }


def build_yearly_report(records):
    """build reports based on year and month"""

    check_record(records)
    yearly_report = {}

    for year, month, amount in records:
        if not year and not month:
            year, month = 2023, 9

        if year not in yearly_report:
            yearly_report[year] = {}

        yearly_report[year][calendar.month_name[month]] = float(amount)

    return yearly_report
