from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_crud, db_models, redis_db
from .flutterwave import rave_pay
from rave_python import Misc, RaveExceptions
from typing import Annotated
import datetime, time
import json
import payments.payment_schema as schemas


redis = redis_db.redis_factory()

router = APIRouter(
    prefix="/bankTransfer",
    tags=["Bank Transfer"],
    responses={
        200: {"description": "Successfull request"},
    },
)


@router.post("/pay")
async def start_bank_transfer(
    invoiceId: str,
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """initaite bank transfer"""

    record = check_invoice(db, invoiceId)
    if record.to_email != active_user["email"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice not assinged to active user",
        )
    first_name, last_name = active_user["name"].split(" ")
    data = {
        "firstname": first_name,
        "lastname": last_name,
        "email": active_user["email"],
        "amount": float(record.price),
    }
    try:
        res = rave_pay.BankTransfer.charge(data)

    except RaveExceptions.TransactionChargeError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=err.err["errMsg"]
        )
    ref_id = "REF-" + str(round(time.time()))
    payment_record = {
        "ref_id": ref_id,
        "flw_ref": res["flwRef"],
        "flw_txRef": res["txRef"],
        "inv_id": record.inv_id,
        "amount": record.price,
        "payment_type": "Bank Transfer",
    }
    db_crud.save(db, db_models.Payments, payment_record)
    redis.set(ref_id, json.dumps(res))
    temp_bank_acc = {
        "ref_id": ref_id,
        "bank_name": res["bankName"],
        "bank_account": res["accountNumber"],
        "expires_in": res["expiresIn"],
        "message": res["transferNote"],
    }
    return temp_bank_acc


def check_invoice(db: Session, invoiceId: str) -> db_models.Invoices:
    """check if the invoice is existing in the db"""

    record = db_crud.get_specific_record(db, db_models.Invoices, inv_id=invoiceId)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching invoice found",
        )

    return record
