# This module contains all helper function needed in processing online payments

from fastapi import HTTPException, status
import datetime


def check_invoice_records(db_record, active_user):
    """checks the record"""

    if db_record.to_email != active_user["email"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice not assigned to active user",
        )

    if datetime.date.today() > db_record.due_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice has expired",
        )
