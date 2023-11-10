# This module contains all helper function needed in processing online payments

from fastapi import HTTPException, status
from models import db_models, db_crud
import datetime


def check_invoice_record(db_record, active_user):
    """checks the record"""

    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching invoice found, check invoice ID",
        )

    if db_record.to_email != active_user["email"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice not assigned to active user",
        )

    if datetime.date.today() > db_record.due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice has expired, can't process payment",
        )


def get_invoice(db, active_user, invoiceId):
    """returns the invoice record"""

    record = db_crud.get_specific_record(
        db, db_models.Invoices, inv_id=invoiceId
    )

    check_invoice_record(record, active_user)
    return record
