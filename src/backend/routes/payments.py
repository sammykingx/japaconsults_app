from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import extract, func
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_crud, db_models, schema
from rave_python import RaveExceptions
from online_payments.flutterwave import rave_pay
from routes_schema import payments_schemas
from docs.routes import payments_response
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
        404: {"description": "Resource Not Found"},
        500: {"description": "Internal server error"},
    },
)


@router.get(
    "/all",
    summary="returns all payments record",
    description="Returns all payment records on the platform. Can be used by "
    "all users irrespective of their roles, the results is been filtered "
    "internally based on the role type of the active user",
    response_model=list[payments_schemas.PaymentResponse],
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

    check_record(records)

    return [payments_serializer(record) for record in records]


@router.get(
    "/pending",
    summary="To see all pending payments on the system",
    description="Use this endpoints to see all pending payments on the "
    "system, can be used by all user roles.",
    response_model=list[payments_schemas.PendingPayments],
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
            #paid=False,
            status="pending",
            payer_email=active_user["email"],
        )

    else:
        records = db_crud.filter_record_in_lifo(
            db, db_models.Payments, db_models.Payments.ref_id, paid=False
        )

    check_record(records)
    return [payments_serializer(record) for record in records]


@router.get(
    "/paid",
    summary="To see all succesful payments on the system",
    description="Use this endpoints to see all paid payments on the "
    "system, can be used by all user roles.",
    response_model=list[payments_schemas.PendingPayments],
)
async def all_paid_payments(
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """return all paid payments"""

    if active_user["role"] == "user":
        records = db_crud.filter_record_in_lifo(
            db,
            db_models.Payments,
            db_models.Payments.paid_at,
            paid=True,
            payer_email=active_user["email"],
        )

    else:
        records = db_crud.filter_record_in_lifo(
            db, db_models.Payments, db_models.Payments.paid_at, paid=True
        )

    check_record(records)
    return [payments_serializer(record) for record in records]


@router.get(
    "/cancelledPayments",
    summary="To see all cancelled payments on the system",
    description="Use this endpoints to see all cancelled payments on the "
    "system, can be used by all user roles.",
    response_model=list[payments_schemas.PendingPayments],
)
async def all_cancelled_payments(
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """return all paid payments"""

    if active_user["role"] == "user":
        records = db_crud.filter_record_in_lifo(
            db,
            db_models.Payments,
            db_models.Payments.ref_id,
            status="cancelled",
            payer_email=active_user["email"],
        )

    else:
        records = db_crud.filter_record_in_lifo(
                db,
                db_models.Payments,
                db_models.Payments.ref_id,
                status="cancelled",
            )

    check_record(records)
    return [payments_serializer(record) for record in records]


@router.get(
    "/verifyPayments",
    summary="Verify's any pending payments",
    description="The transaction reference 'refId' is passed as "
    "query parameter in verifying if a payment was successfull.Once "
    "it's successful, the payment record is updated.",
    include_in_schema=False,
)
async def reVerify_payments(
    refId: str,
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """re_validates payments"""

    record = db_crud.get_specific_record(
                    db, db_models.Payments, ref_id=refId
                )

    check_record(record)
    # make a network call to verify payment

    raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Endpoint still in development",
        )


@router.get(
    "/totalRevenue",
    summary="Returns the total revenue on the system",
    description="Returns the total revenue generated based on month"
    "should be used by previledged users",
    responses=payments_response.total_revenue_response,
)
async def total_revenue(
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """returns the total revenue"""

    if active_user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unathorized access to resource",
        )

    # if month:
    #    if month <= 0 or month > 12:
    #        raise HTTPException(
    #            status_code=status.HTTP_400_BAD_REQUEST,
    #            detail="month should be within 1 to 12",
    #        )

    #    else:
    #        records = (
    #            db.query(db_models.Invoices)
    #            .filter(
    #                extract("month", db_models.Invoices.paid_at) == month,
    #                extract("year", db_models.Invoices.paid_at) == year,
    #            )
    #            .all()
    #        )

    try:
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
            .filter(db_models.Invoices.paid == True)
            .group_by("year", "month")
            .all()
        )

    except Exception as err:
        # send mail
        print(f"Error at total revenue endpoint: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="encountered some issues while processing request",
        )

    data = build_yearly_report(records)

    return data


@router.get(
    "/totalSpend",
    summary="Returns the total amount spent by a user",
    description="Returns the total amount spent by a user on the platform. "
    "should not be used by previledged users",
    response_model=payments_schemas.UserTotalSpend,
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

    records = db_crud.get_by(
        db, db_models.Invoices, to_email=active_user["email"], paid=True
    )

    spent_amount = sum(record.price for record in records if record.paid)

    return {
        "name": active_user["name"],
        "email": active_user["email"],
        "total_spend": spent_amount,
    }


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
        "title": record.title,
        "rave_txref": record.flw_txRef,
        "paid_by": record.paid_by,
        "amount": record.amount,
        "paid": record.paid,
        "status": record.status,
        "paid_at": record.paid_at,
        "payer_email": record.payer_email,
        "payment_type": record.payment_type,
    }


def build_yearly_report(records):
    """build reports based on year and month"""

    yearly_report = {}

    for year, month, amount in records:
        if not year and not month:
            year, month = 2023, 9

        if year not in yearly_report:
            yearly_report[year] = {}

        yearly_report[year][calendar.month_name[month]] = float(amount)

    return yearly_report
