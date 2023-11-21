from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_crud, db_models, redis_db
from .flutterwave import rave_pay
from rave_python import RaveExceptions
from typing import Annotated
from online_payments import payments_utils
from dotenv import load_dotenv
import online_payments.payment_schema as schemas
import datetime, json, time, os


redis = redis_db.redis_factory()

router = APIRouter(
    prefix="/bankTransfer",
    tags=["Bank Transfer"],
    responses={
        200: {"description": "Successfull request"},
    },
)

load_dotenv()
HEADER = {
    "Authorization": "Bearer {}".format(os.getenv("LIVE_SECRET_KEY")),
}


@router.get(
    "/pay",
    summary="Initiates bank transfer payment method",
    description="Use this payment method to start bank transfer payments. "
    "It returns the transaction ref_id and the temporay bank "
    "details the user should make payments to.",
    response_model=schemas.BankTransferResponse,
    include_in_schema=False,
)
async def start_bank_transfer(
    invoiceId: str,
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """initiate bank transfer"""

    record = payments_utils.validate_invoice(
                    db, active_user["email"], invoiceId
                )

    ref_id = "REF-" + str(round(time.time()) * 2)
    data = {
        "tx_ref": "MC-1585230950508",
        "email": active_user["email"],
        "amount": float(record.price),
        "fullname": active_user["name"],
        "currency": "NGN",
        "narration": record.title,
    }

    response = get_virtual_account(data)

    payment_record = payments_utils.payment_serializer(
                            ref_id,
                            res,
                            record,
                            active_user,
                            "bank transfer"
                    )

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


@router.get(
    "/verifyTransfer",
    summary="Use this endpoint To verify all bank transfer transactions",
    description="This endpoint is used to verify if a users bank transfer "
    "is successful. You should pass the ref_id gotten from "
    "the pay endpoint as query params.",
    response_model=schemas.VerifyBankTransfer,
    include_in_schema=False,
)
async def verify_bank_transfer(
    refId: str,
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """verify bank transfer"""

    if not redis.exists(refId):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reference id to continue verification process",
        )

    data = json.loads(redis.get(refId))

    try:
        res = rave_pay.BankTransfer.verify(data["txRef"])

    except RaveExceptions.TransactionVerificationError as err:
        payments_utils.cancell_transaction(db, refId)
        redis.delete(refId)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err.err["errMsg"],
        )

    redis.delete(refId)
    payments_utils.successfull_transaction(db, refId)

    return {
        "msg": "Transfer successfull",
        "transactionComplete": res["transactionComplete"],
    }


def get_virtual_account(user_data) -> dict:
    """gets virtual account details"""

    try:
        response = req.post(
            os.getenv("BANK_TRANSFER_ENDPOINT"),
            headers=HEADER,
            body=user_data,
            timeout=5,
        ).json()

    except req.exceptions.ConnectionError:
        raise HTTException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="ERROR: check internet connection",
        )

    except req.exceptions.ReadTimeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="payment processor took too long to respond",
        )

    return response
