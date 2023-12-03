from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_crud, db_models, schema
from routes_schema import invoice_schema
from online_payments import payments_utils
from datetime import date, datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr
import time

router = APIRouter(
    prefix="/invoice",
    tags=["Invoice"],
    responses={
        200: {"description": "Successful response"},
        201: {"description": "Invoice created"},
        400: {"description": "Missing required data to process request"},
        401: {"description": "Unauthorized access to resource"},
        403: {"description": "Cannot access resource"},
        404: {"description": "Resource Not Found"},
        500: {"description": "Internal server error"},
    },
)


@router.get(
    "/all",
    summary="Returns all created invoices",
    description="This endpoints can be used by previledged and normal users",
    response_model=list[invoice_schema.InvoiceResponse],
)
async def get_all_invoice(
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """get all invoices created"""

    if active_user["role"] == "user":
        records = db_crud.filter_record_in_lifo(
            db,
            db_models.Invoices,
            db_models.Invoices.created_at,
            to_email=active_user["email"],
        )

    else:
        records = db_crud.all_record_in_lifo(
            db,
            db_models.Invoices,
            db_models.Invoices.created_at,
        )

    is_empty(records)

    data = [invoice_serializer(record) for record in records]
    return data


@router.get(
    "/pending",
    summary="Returns all unpaid invoices",
    description="This endpoint can be used by all users, no restrictions",
    response_model=list[invoice_schema.InvoiceResponse],
)
async def get_pending_invoices(
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """returns all unpaid invoices"""

    if active_user["role"] == "user":
        records = db_crud.filter_record_in_lifo(
            db,
            db_models.Invoices,
            db_models.Invoices.created_at,
            paid=False,
            status=None,
            to_email=active_user["email"],
        )

    else:
        records = db_crud.filter_record_in_lifo(
            db,
            db_models.Invoices,
            db_models.Invoices.created_at,
            paid=False,
            status=None,
        )

    is_empty(records)

    data = [invoice_serializer(record) for record in records]
    return data


@router.get(
    "/expired",
    summary="Returns all expiredd invoices",
    description="This endpoint can be used by all users, no restrictions",
    response_model=list[invoice_schema.InvoiceResponse],
)
async def get_pending_invoices(
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """returns all expired invoices"""

    if active_user["role"] == "user":
        records = db_crud.filter_record_in_lifo(
            db,
            db_models.Invoices,
            db_models.Invoices.created_at,
            status="expired",
            to_email=active_user["email"],
        )

    else:
        records = db_crud.filter_record_in_lifo(
            db,
            db_models.Invoices,
            db_models.Invoices.created_at,
            status="expired",
        )

    is_empty(records)

    data = [invoice_serializer(record) for record in records]
    return data


@router.get(
    "/paidInvoice",
    summary="returns all paid invoices",
    description="Use this endpoint to get all paid invoices both for users "
    "and previledged users. To get all paid invoices by the "
    "active user, pass the email of user as query parameter.",
    response_model=list[invoice_schema.InvoiceResponse],
)
async def get_paid_invoice(
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """returns all paid invoices"""

    if active_user["role"] == "user":
        records = db_crud.filter_record_in_lifo(
            db,
            db_models.Invoices,
            db_models.Invoices.paid_at,
            to_email=active_user["email"],
            paid=True,
        )

    else:
        records = db_crud.filter_record_in_lifo(
            db,
            db_models.Invoices,
            db_models.Invoices.paid_at,
            paid=True,
        )

    is_empty(records)

    data = [invoice_serializer(record) for record in records]
    return data


@router.get(
    "/{invoiceId}",
    summary="Returns a specific invoice by its id",
    description="This endpoint can be used by all users",
    response_model=invoice_schema.InvoiceResponse,
)
async def get_invoice_by_id(
    invoiceId: str,
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """gets an invoice by its id"""

    record = db_crud.get_specific_record(
        db, db_models.Invoices, inv_id=invoiceId
    )

    is_empty(record)
    data = invoice_serializer(record)
    return data


@router.post(
    "/create",
    summary="Creates invoice",
    description="Creates invoice, should not be used by 'user' roles",
    status_code=status.HTTP_201_CREATED,
)
async def create_invoice(
    payload: schema.CreateInvoice,
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """creates invoice"""

    if active_user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access to resource",
        )

    check_payload(payload)
    record = db_crud.get_specific_record(
        db, db_models.User, email=payload.to_email
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user with matching email found",
        )
    if active_user["email"] == payload.to_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot send Invoice to yourself",
        )
    data = payload.model_dump().copy()
    data.update(
        {
            "inv_id": "JPC-" + str(round(time.time())),
            "created_at": datetime.utcnow(),
            "created_by": active_user["name"],
            "status": "pending",
        }
    )
    db_crud.save(db, db_models.Invoices, data)
    if data.get("to_email", None):
        # send user an email for new invoice
        print("sending a mail here")

    return {"msg": "Invoice created", "invoiceId": data["inv_id"]}


@router.put(
    "/update",
    summary="updates the fields of an invoice",
    description="This endpoint should not be used by users with role type 'user'.",
)
async def update_invoice(
    payload: invoice_schema.UpdateInvoice,
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """updates the invoice with the payload data"""

    if active_user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access to resource",
        )

    check_payload(payload)
    record = db_crud.get_specific_record(
        db, db_models.Invoices, inv_id=payload.inv_id
    )

    is_empty(record)

    # update db record
    if record.paid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can't Update an already paid invoice",
        )

    record.title = payload.title
    record.desc = payload.desc
    record.price = payload.price
    record.due_date = payload.due_date
    record.updated_at = datetime.utcnow()
    record.updated_by = active_user["name"]

    db.commit()
    db.refresh(record)

    # send to_email  email on updated invoice
    return {"msg": "Invoice Updated"}


@router.patch(
    "/manualUpdate",
    summary="Manually change the invoice status to paid.",
    description="Changes the invoice status to paid. should only be used by admin.",
)
async def manual_invoice_status_update(
    invoiceId: str,
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """updates the payment status of an invoice to paid"""

    if active_user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access to resource",
        )

    invoice_record = db_crud.get_specific_record(
        db, db_models.Invoices, inv_id=invoiceId
    )

    is_empty(invoice_record)

    payment_record = db_crud.get_specific_record(
        db, db_models.Payments, inv_id=invoiceId
    )

    if not payment_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No existing transaction ref for invoice",
        )

    payment_timestamp = datetime.utcnow()

    # payments_utils.update_payments_to_paid(
    #    payment_record, payment_timestamp
    # )

    payments_utils.update_invoice_status(
        db,    
        invoice_record,
        "paid",
    )

    # db.refresh(invoice_record)
    # db.refresh(payment_record)

    return {"msg": "Invoice status updated manaually"}


@router.delete(
    "/thrashInvoice",
    summary="Deletes invoice from the system",
    description="Removes invoice from the system, should be used by admin or managers",
)
async def delete_invoice(
    invoiceId: str,
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """removes an invoice by id"""

    if active_user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access to resource",
        )
    db_crud.delete(db, db_models.Invoices, inv_id=invoiceId)
    return {"msg": "Deleted successfully"}


def check_payload(payload: schema.CreateInvoice) -> None:
    """checks the user payload"""

    if len(payload.title) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="number of characters in 'title' greater than 50",
        )

    if len(payload.desc) > 250:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="number of characters is greater than 100",
        )

    price = str(payload.price)

    if len(price.split(".")[1]) > 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of digits of decimal must be less than 2",
        )

    if payload.due_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Due date must be greater than current date",
        )


def is_empty(data: db_models.Invoices):
    """checks if record is empty"""

    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No Invoices found",
        )


def invoice_serializer(record: db_models.Invoices):
    """serilize invoice"""

    return {
        "inv_id": record.inv_id,
        "title": record.title,
        "status": record.status,
        "desc": record.desc,
        "price": record.price,
        "to_email": record.to_email,
        "created_at": record.created_at,
        "created_by": record.created_by,
        "updated_at": record.updated_at,
        "updated_by": record.updated_by,
        "due_date": record.due_date,
        "paid": record.paid,
        "paid_at": record.paid_at,
        "rave_txref": record.flw_txref,
        "ref_id": record.ref_id,
    }
