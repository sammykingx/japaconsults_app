# This module contains all helper function needed in processing online payments
# The db variable used as parameter signifies the request db session

from fastapi import HTTPException, status
from models import db_models, db_crud
import datetime


def validate_invoice(db, email, invoiceId):
    """validates invoice record"""

    invoice_record = get_invoice(db, invoiceId)
    is_empty(invoice_record)
    check_assignee(email, invoice_record)
    is_expired(invoice_record)
    has_active_payment(db, invoiceId)
    return invoice_record


def has_active_payment(db, invoiceId):
    """checks if the user has an active payment process"""

    payment_records = db_crud.get_by(
        db, db_models.Payments, inv_id=invoiceId
    )

    if not payment_records:
        return False

    for record in payment_records:
        if record.status == "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{record.ref_id} still active, kindly complete "
                       "transaction",
            )


def check_assignee(email, record):
    """checks if the invoice is assigned to active_user"""

    if record.to_email != email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice not assigned to active user",
        )


def is_expired(db_record):
    """checks if the invoice has expired"""

    if datetime.date.today() > db_record.due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice has expired, can't process payment",
        )


def is_empty(db_record):
    """checks the db record if its empty"""

    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching invoice found, check invoice ID",
        )


def get_invoice(db, invoiceId):
    """returns the invoice record"""

    record = db_crud.get_specific_record(
        db, db_models.Invoices, inv_id=invoiceId
    )

    return record


def get_payments_record(db, refId):
    """gets the payment record

        db: the request db session
        refId: the payment reference id
    """

    record = db_crud.get_specific_record(
        db, db_models.Payments, ref_id=refId
    )

    return record


def cancell_transaction(db, refId):
    """ changes the payments status to cancelled

        db: the request db session
        refId: the payment reference id
    """

    payment_record = get_payments_record(db, refId)
    payment_record.status = "cancelled"
    db.commit()
    db.refresh(payment_record)


def update_invoice_to_paid(
    invoice_record,
    payment_record,
    payment_timestamp,
):
    """updates invoices record to paid"""

    invoice_record.paid = True
    invoice_record.ref_id = payment_record.ref_id
    invoice_record.flw_txref = payment_record.flw_txRef
    invoice_record.paid_at = payment_timestamp


def update_payments_to_paid(payment_record, payment_timestamp):
    """updates the payment record to paid"""

    payment_record.paid = True
    payment_record.paid_at = payment_timestamp
    payment_record.status = "paid"


def successfull_transaction(db, refId):
    """updates the payments and invoice table upon successfull payments"""

    payment_timestamp = datetime.datetime.utcnow()

    # get records
    payment_record = get_payments_record(db, refId)
    invoice_record = get_invoice(db, payment_record.inv_id)

    # update records
    update_payments_to_paid(payment_record, payment_timestamp)
    update_invoice_to_paid(
            invoice_record, payment_record, payment_timestamp
        )

    db.commit()

    db.refresh(payment_record)
    db.refresh(invoice_record)

    return invoice_record


def payment_serializer(ref_id, resp, record, active_user, payment_type):
    """serializes the payment record"""

    return {
        "ref_id": ref_id,
        "flw_ref": resp["flwRef"],
        "flw_txRef": resp["txRef"],
        "inv_id": record.inv_id,
        "title": record.title,
        "amount": record.price,
        "payer_email": active_user["email"],
        "paid_by": active_user["name"],
        "payment_type": payment_type,
        "status": "pending",
    }
