from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_crud, db_models, redis_db
from .flutterwave import rave_pay
from rave_python import Misc, RaveExceptions
from typing import Annotated
import datetime, time
import json
from online_payments import payments_utils
import online_payments.payment_schema as schemas


redis = redis_db.redis_factory()

router = APIRouter(
    prefix="/card",
    tags=["card Paymemnts"],
    responses={
        200: {"description": "Successfule Request"},
        400: {"description": "Missing required/Invalid data in request"},
    },
)


@router.post(
    "/pay",
    summary="Initiates card payment process for the active user.",
    description="Should be used for processing card payments",
    response_model=schemas.CardResponse,
)
async def card_payments(
    invoiceId: str,
    payload: schemas.CardPayments,
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """collect card payments"""

    # check payload

    # record = db_crud.get_specific_record(
    #    db, db_models.Invoices, inv_id=invoiceId
    # )

    # if not record:
    #    raise HTTPException(
    #        status_code=status.HTTP_404_NOT_FOUND,
    #        detail="No matching invoice found, check invoice id",
    #    )

    # gets and perform checks on the invoice ID
    record = payments_utils.get_invoice(db, active_user, invoiceId)

    card_details = payload.model_dump().copy()
    f_name, l_name = active_user["name"].split(" ")
    card_details.update(
        email=active_user["email"],
        amount=float(record.price),
        firstname=f_name,
        lastname=l_name,
        # suggested_auth="PIN",
    )

    try:
        res = rave_pay.Card.charge(card_details)
        if res["suggestedAuth"]:
            if res["suggestedAuth"] != "PIN":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{res['suggestedAuth']} authentication not supported",
                )

            card_details.update(suggested_auth="PIN")
            res = rave_pay.Card.charge(card_details)

    except RaveExceptions.CardChargeError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.err["errMsg"],
        )

    ref_id = "REF-" + str(round(time.time()))
    new_record = {
        "ref_id": ref_id,
        "flw_ref": res["flwRef"],
        "flw_txRef": res["txRef"],
        "inv_id": invoiceId,
        "amount": float(record.price),
        "payer_email": active_user["email"],
        "paid_by": active_user["name"],
        "payment_type": "card",
        "status": "Pending",
    }
    db_crud.save(db, db_models.Payments, new_record)
    redis.set(ref_id, json.dumps(res))
    return {
        "ref_id": ref_id,
        "validationRequired": res["validationRequired"],
    }


@router.post(
    "/verify",
    summary="Used to verify card payments",
    description="This method is called to verify the users payments. The otp "
    "sent by the user's bank should be sent alongside the payment ref_id "
    "gotten from pay endpoint.",
)
async def verify_card_payments(
    payload: schemas.VerifyCardPayments,
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """veriy's card payments"""

    # check if the ref_id exist on redis
    if not redis.exists(payload.ref_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reference id to continue verification process",
        )

    data = json.loads(redis.get(payload.ref_id))
    rave_flwRef = data["flwRef"]
    rave_txRef = data["txRef"]

    payment_record = db_crud.get_specific_record(
        db, db_models.Payments, ref_id=payload.ref_id
    )

    try:
        res = rave_pay.Card.validate(rave_flwRef, payload.otp)
        res = rave_pay.Card.verify(rave_txRef)

    except RaveExceptions.TransactionValidationError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.err["errMsg"],
        )
    except RaveExceptions.TransactionVerificationError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.err["errMsg"],
        )
    # get successfull payment timestamp
    payment_timestamp = datetime.datetime.utcnow()

    # delete key from redis
    redis.delete(payload.ref_id)

    invoice_record = db_crud.get_specific_record(
        db, db_models.Invoices, inv_id=payment_record.inv_id
    )

    # update payments
    payment_record.paid = True
    payment_record.paid_at = payment_timestamp
    payment_record.status = "Paid"

    # update invoice
    invoice_record.paid = True
    invoice_record.paid_at = payment_timestamp

    db.commit()

    db.refresh(payment_record)
    db.refresh(invoice_record)

    return {
        "transactionComplete": True,
        "ref_id": payload.ref_id,
        "inv_id": invoice_record.inv_id,
        "amount": res["amount"],
        "chargedamount": res["chargedamount"],
        "currency": res["currency"],
    }


# async def get_record(db,)
