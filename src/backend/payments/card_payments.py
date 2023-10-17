from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_crud, db_models, redis_db
from .flutterwave import rave_pay
from rave_python import RaveExceptions
from typing import Annotated
import datetime, time
import json
import payments.payment_schema as schemas 


redis = redis_db.redis_factory()

router = APIRouter(
        prefix="/card",
        tags=["card Paymemnts"],
        responses={
            200: {"description": "Successfule Request"},
        }
    )

@router.post(
        "/pay",
        summary="For card payments only",
        description="Should be used for processing card payments")
async def card_payments(
        invoiceId: str,
        payload: schemas.CardPayments,
        active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
        db: Annotated[Session, Depends(db_engine.get_db)]
    ):
    """collect card payments"""

    # check payload

    record = db_crud.get_specific_record(db, db_models.Invoices, inv_id=invoiceId)
    if not record:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching invoice found, check invoice id"
            )

    card_details = payload.model_dump().copy()
    card_details.update(
            email=active_user["email"],
            firstname=active_user["name"],
            suggested_auth="PIN")
    print(card_details)
    try:
        res = rave_pay.Card.charge(card_details)

    except RaveExceptions.CardChargeError as err:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err.err["errMsg"]
            )
    ref_id = "REF-" + str(round(time.time()))
    new_record = {
            "ref_id": ref_id,
            "flw_ref": res["flwRef"],
            "flw_txRef": res["txRef"],
            "inv_id": invoiceId,
            "amount": card_details["amount"],
            "payment_type": "card",
        }
    db_crud.save(db, db_models.Payments, new_record)
    redis.set(ref_id, json.dumps(res))
    return {"ref_id": ref_id, "validationRequired": res["validationRequired"]}
