from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_crud, db_models, redis_db
from online_payments import flutterwave, payments_utils, payment_schema
from dotenv import load_dotenv
from typing import Annotated
import requests as req
import json, os, time


router = APIRouter(
    prefix="/flutterwave",
    tags=["Flutterwave"],
    responses={
        400: {
            "description": "Bad/Invalid request",
        },

        500: {
            "description": "Internal server error",
        }
    },
)

redis = redis_db.redis_factory()

load_dotenv()

HEADER = flutterwave.HEADER


@router.get(
    "/checkoutModal",
    summary="Creates payments link users use in processing payments.",
    description="The invoice ID should be passed as query parameter"
    "and then a checkout url is generated for user payment."
    "The user should be redirected to this link for payments."
    "The link generated is a livelink, so don't put real stuffs",
    response_model=payment_schema.RaveCheckoutResponse,
)
async def rave_checkout(
    invoiceId: str,
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """exchange invoice ID for payment url"""

    record = payments_utils.validate_invoice(
                    db, active_user["email"], invoiceId
                )

    customer = {
        "name": active_user["name"],
        "email": active_user["email"],
    }

    ref_id = "REF-" + str(round(time.time()) * 2)
    user_payload = build_payment_payload(
        ref_id, float(record.price), customer
    )

    response = get_rave_link(user_payload)
    pay_link = response["data"]["link"]

    serialized_data = payments_utils.payment_serializer(
                            ref_id, record, active_user, "rave_modal"
                        )

    db_crud.save(db, db_models.Payments, serialized_data)
    redis.set(ref_id, json.dumps(serialized_data))

    return {
        "ref_id": ref_id,
        "status": response["status"],
        "link": response["data"]["link"],
        "link_type": response["message"],
    }


@router.get(
    "/callback",
    summary="Verify's if the users payment was successful",
    description="This endpoint is automatically called by payment processor"
    " after user completes payment process. We then verify the"
    " the users payments if it was successful or cancelled",
    response_model=payment_schema.CallbackResponse,
)
async def rave_checkout_callback(
    req_url: Request,
    bg_task: BackgroundTasks,
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """Verify's user payments"""

    query_params = str(req_url.query_params)
    params = dict(item.split("=") for item in query_params.split("&"))

    #print(params)

    payment_record = payments_utils.get_payments_record(
                            db, params.get("tx_ref")
                        )

    # status can be cancelled, failed, completed.
    if params.get("status") == "cancelled":
        payments_utils.update_payment_status(
            db, payment_record, "cancelled"
        )

        redis.delete(params.get("tx_ref"))
        return {
                "status": params.get("status"),
                "ref_id": params.get("tx_ref"),
            }

    elif params.get("status") == "failed":
        payments_utils.update_payment_status(
            db, payment_record, "failed"
        )

        redis.delete(params.get("tx_ref"))
        return {
                "status": params.get("status"),
                "ref_id": params.get("tx_ref"),
            }

    # change transaction to checking awaiting call to verification endpoint
    payments_utils.change_to_checking(
        db, payment_record, params.get("transaction_id"), "checking"
    )

    # update redis key to add transaction_id
    payments_utils.add_transaction_id_to_redis_key(
            params.get("tx_ref"), params.get("transaction_id")
        )

    # add backg_round job to verify transaction
    bg_task.add_task(
        payments_utils.confirm_user_payments,
        params.get("tx_ref"),
        HEADER
    )

    return {
            "status": params.get("status"),
            "ref_id": params.get("tx_ref"),
        }

# demo reponse params
# status=completed&tx_ref=REF-3400515214&transaction_id=1141230276


@router.get(
    "/paymentCallback",
    summary="checks the transaction status immediately after user payment",
    description="This endpoint should be called by the frontend immediately"
    " after user completes payment process. The backend then verify's the"
    " the users payments if it was cancelled, completed or failed",
    response_model=payment_schema.CallbackResponse,
)
async def payment_callback(
    tx_ref: str,
    tx_status: str,
    bg_task: BackgroundTasks,
    db: Annotated[Session, Depends(db_engine.get_db)],
    transaction_id: int | None = None,
):
    """payment callback to verify payment

    @tx_ref: the tx_ref mathes the ref_id attahed to payload during checkout
    @tx_status: the status of the users payments
    @transaction_id: only present when status param is completed
    """

    check_parameter_integrity(tx_ref, tx_status, transaction_id)

    payment_record = payments_utils.get_payments_record(
                            db, tx_ref
                        )

    if tx_status == "cancelled":
        payments_utils.update_payment_status(
            db, payment_record, "cancelled"
        )

        redis.delete(tx_ref)
        return {
                "status": tx_status,
                "ref_id": tx_ref,
            }

    elif tx_status == "failed":
        payments_utils.update_payment_status(
            db, payment_record, "failed"
        )

        redis.delete(tx_ref)

    payments_utils.change_to_checking(
            db, payment_record, transaction_id, "checking"
        )

    payments_utils.add_transaction_id_to_redis_key(
            tx_ref, transaction_id
        )

    bg_task.add_task(
        payments_utils.confirm_user_payments,
        tx_ref,
        HEADER
    )

    return {
            "status": tx_status,
            "ref_id": tx_ref,
        }


@router.get(
    "/verifyPayments",
    summary="Verify's if the users payment was successful",
    description="This endpoint verifies the users payment status "
                "with payment processor before the record is updated."
                "Should be called in situations where there's delay"
                " from users bank in validating payments.",
    response_model=payment_schema.RaveVerifyPayments,
)
async def verify_user_payments(refId: str) -> dict:
    """verifies the users payments with rave"""

    if not redis.exists(refId):
        return {
                "status": "completed",
                "msg": "payment verification complete",
            }

    response = payments_utils.confirm_user_payments(refId, HEADER)
    redis.delete(refId)

    return response


def get_rave_link(user_payload) -> dict:
    """makes the network call to flutterwave api"""

    try:
        response = req.post(
            os.getenv("CHECKOUT_ENDPOINT"),
            headers=HEADER,
            json=user_payload,
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


def build_payment_payload(
    flw_txref: str, price: float, customer: dict
) -> dict:
    """builds the user payload for api call"""

    payload = {
        "tx_ref": flw_txref,
        "amount": price,
        "customer": customer,
        "redirect_url": "http://localhost:5000/flutterwave/callback",
        #"redirect_url": "https://japaconsults.sammykingx.tech/raveCheckout/callback",
        "customizations": {
            "title": "sammykingx-japaconsults",
            "logo": "https://japaconsults.com/wp-content/"
            "uploads/2021/05/LogoMakr-6zrJ19.png",
        },
    }

    return payload


def check_parameter_integrity(tx_ref, tx_status, transaction_id):
    """checks integrity of query params"""

    if not redis.exists(tx_ref):
         raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid tx_ref value, check and try again",
            )

    if tx_status not in ("cancelled", "completed", "failed"):
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unrecognized transaction status => '{tx_status}'",
            )

    if tx_status == "completed" and transaction_id == None:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"transaction id can't be empty when tx_status is "
                        "completed",
            )
