from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_crud, db_models, redis_db
from .flutterwave import HEADER
from typing import Annotated
from online_payments import payments_utils
from .rave_checkout import router
from dotenv import load_dotenv
import online_payments.payment_schema as schemas
import json, time, requests, os


redis = redis_db.redis_factory()

load_dotenv()


@router.get(
    "/bankTransfer",
    summary="Initiates bank transfer payment method",
    description="Use this payment method to start bank transfer payments. "
    "It returns the transaction ref_id and the temporay bank "
    "details the user should make payments to.",
    response_model=schemas.BankTransferResponse,
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
        "tx_ref": ref_id,
        "email": active_user["email"],
        "amount": float(record.price),
        "fullname": active_user["name"],
        "currency": "NGN",
    }

    resp = get_virtual_account(data)
    data.update(resp["meta"]["authorization"])

    print("\nref_id => ", ref_id)
    print("\nrave_resp =>", resp)

    payment_record = payments_utils.payment_serializer(
        ref_id,
        record,
        active_user,
        "direct bank transfer",
        resp["meta"]["authorization"]["transfer_reference"],
    )

    db_crud.save(db, db_models.Payments, payment_record)
    redis.set(ref_id, json.dumps(data))
    temp_bank_acc = {
        "ref_id": ref_id,
        "message": resp["message"],
        "bank_name": resp["meta"]["authorization"]["transfer_bank"],
        "bank_account": resp["meta"]["authorization"][
            "transfer_account"
        ],
        "transfer_amount": resp["meta"]["authorization"][
            "transfer_amount"
        ],
        "expires_in": resp["meta"]["authorization"][
            "account_expiration"
        ],
    }

    return temp_bank_acc


def get_virtual_account(user_data) -> dict:
    """gets virtual account details"""

    try:
        response = requests.post(
            os.getenv("BANK_TRANSFER_ENDPOINT"),
            headers=HEADER,
            data=user_data,
            timeout=10,
        ).json()

    except requests.exceptions.ConnectionError:
        raise HTTException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="ERROR: check internet connection",
        )

    except requests.exceptions.ReadTimeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="payment processor took too long to respond",
        )

    return response
