from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_crud, db_models, schema
from datetime import date, datetime
from typing import Annotated
from pydantic import BaseModel, EmailStr
import time

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
    }
)

@router.get(
    "/all",
    summary="returns all payments record",
    description="Should be used by previledged users only in seeing "\
                "payment details ",)
async def app_payments(
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """get all payments records"""
    
    if active_user["role"] == "user":
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized access to resource",
            )

    if active_user["role"] == "user":
        records = ( db.query(db_models.Payments)
                    .filter_by(payer_email=active_user["email"])
                    .order_by(db_models.Payments.paid_at.desc())
                    .all()
                )
    
    else:
        records = db_crud.all_record_in_lifo(
            db, db_models.Payments, db_models.Payments.paid_at
        )

    if not records:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No payment record found",
            )

    return [payments_serializer(record) for record in records]


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
