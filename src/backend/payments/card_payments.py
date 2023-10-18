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
        description="Should be used for processing card payments",
        response_model=schemas.CardResponse)
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
            amount=float(record.price),
            firstname=active_user["name"],
            suggested_auth="PIN",)
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
            "amount": float(record.price),
            "payment_type": "card",
        }
    db_crud.save(db, db_models.Payments, new_record)
    redis.set(ref_id, json.dumps(res))
    return {"ref_id": ref_id, "validationRequired": res["validationRequired"]}


@router.post(
        "/verify",
        summary="Used to verify card payments",
        description="This method is called to verify the users payments")
async def verify_card_payments(
        payload: schemas.VerifyCardPayments,
        active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
        db: Annotated[Session, Depends(db_engine.get_db)],
):
    """veriy's card payments"""

    # check if the ref_id exist in redis then check db if it doesnt
    if not redis.exists(payload.ref_id):
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching reference id found to continue transaction"
            )
    data = json.loads(redis.get(payload.ref_id))
    rave_flwRef = data["flwRef"]
    rave_txRef = data["txRef"]
#    else:
    record = db_crud.get_specific_record(
            db, db_models.Payments, ref_id=payload.ref_id
        )
#        rave_flwRef = record.flw_ref
#        rave_txRef = record.flw_txRef
    if not record:
            raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No matching reference id found to continue transaction")
    try:
        res = rave_pay.Card.validate(rave_flwRef, payload.otp)
        print("validate =", res)
        res = rave_pay.Card.verify(rave_txRef)

    except RaveExceptions.TransactionValidationError as err:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err.err["errMsg"]
            )
    except RaveExceptions.TransactionVerificationError as err:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err.err["errMsg"]
            )
    # update the payments table and invoic table
    redis.delete(payload.ref_id)
    return {"transactionComplete": True,
            "ref_id": payload.ref_id,
            "amount": res["amount"],
            "chargedamount": res["chargedamount"],
            "currency": res["currency"],}
    # call validate with otp to match
    # then verify to match


#async def get_record(db,)
