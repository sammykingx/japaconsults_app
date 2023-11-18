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
from online_payments import payments_utils, payment_schema
from dotenv import load_dotenv
from typing import Annotated
import requests as req
import json, os, time


router = APIRouter(
    prefix="/raveCheckout",
    tags=["Flutterwave Checkout"],
    responses={
        500: {
            "description": "Internal server error",
        }
    },
)

redis = redis_db.redis_factory()

load_dotenv()

HEADER = {
    "Authorization": "Bearer {}".format(os.getenv("LIVE_SECRET_KEY")),
}


@router.get(
    "/pay",
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

    #our_ref_id = "REF-" + str(round(time.time()) * 2)
    #serialized_data = serialize_to_db(
    #    active_user, ref_id, pay_link, record
    #)

    serialized_data = payments_utils.payment_serializer(
                            ref_id, record, active_user, "rave_modal"
                        )

#    redis.set(ref_id, json.dumps(serialized_data))

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
)
async def rave_checkout_callback(
    req_url: Request,
    bg_task: BackgroundTasks,
    #active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """Verify's user payments"""

   # raise HTTPException(
   #     status_code=status.HTTP_501_NOT_IMPLEMENTED,
   #     detail="Endpoint still in development",
   # )

    query_params = str(req_url.query_params)
    params = dict(item.split("=") for item in query_params.split("&"))

    print(params)

    # status can be cancelled, failed,
    if params.get("status") == "cancelled":
        # update record with txref to cancelled
        payment_record = payments_utils.cancell_transaction(
                                db, params.get("tx_ref"))

        redis.delete(params.get("tx_ref"))
        return {
                "status": params.get("status"),
                "ref_id": params.get("tx_ref"),
            }

    elif params.get("status") == "failed":
        payment_record = payments_utils.failed_transaction(
                                db, params.get("tx_ref"))

        redis.delete(params.get("tx_ref"))
        return {
                "status": params.get("status"),
                "ref_id": params.get("tx_ref"),
            }

    # change transaction to checking awaiting call to verification endpoint
    payment_record = payments_utils.change_to_checking(
                            db,
                            params.get("tx_ref"),
                            params.get("transaction_id"),
                        )
    # update redis key to add transaction_id
    payments_utils.add_transaction_id_to_redis_key(
            refId, params.get("transaction_id")
        )

    # add background job to verify transaction

    return {
            "status": payment_record.status,
            "ref_id": params.get("tx_ref"),
        }

    return query_params

# demo reponse params
# status=completed&tx_ref=REF-3400515214&transaction_id=1141230276

def get_rave_link(user_payload):
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
        "redirect_url": "http://localhost:5000/raveCheckout/callback",
        #"redirect_url": "https://japaconsults.sammykingx.tech/raveCheckout/callback",
        "customizations": {
            "title": "sammykingx-japaconsults",
            "logo": "https://japaconsults.com/wp-content/"
            "uploads/2021/05/LogoMakr-6zrJ19.png",
        },
    }

    return payload


#def serialize_to_db(active_user, ref_id, pay_link, record):
#    """serialize the user data to db format"""
#
#    live mode
#    flw_ref = pay_link.removeprefix(
#        "https://checkout.flutterwave.com/v3/hosted/pay/"
#    )

#    test mode
#    flw_ref = pay_link.split("/hosted/pay/")[-1]

#    all_ref = {"flwRef": flw_ref, "txRef": flw_txref}

#    serialized_data = payments_utils.payment_serializer(
#                            ref_id,
#                            flw_ref,
#                            record,
#                            active_user,
#                            "rave modal"
#                    )
#
#    return serialized_data


def verify_payments_with_rave(refId):
    """verify if the user payment is succssfull or not"""

    if not redis.exists(refId):
        raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid reference id",
                )
    # mak the api call
    resp = payments_utils.verv_api_call(refid, HEADER,)

    # check the resp status, check chargd_amount
    # get the transaction id, flw_ref, payment_type

