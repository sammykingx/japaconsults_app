from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_crud, db_models
from online_payments import payments_utils, payment_schema
from dotenv import load_dotenv
from typing import Annotated
import requests as req
import os, time


router = APIRouter(
    prefix="/raveCheckout",
    tags=["Flutterwave Checkout"],
    responses={
        500: {
            "description": "Internal server error",
        }
    },
)

CHECKOUT_ENDPOINT = "https://api.flutterwave.com/v3/payments"

VERIFY_PAYMENT_ENDPOINT = (
    "https://api.flutterwave.com/v3/transactions/verify_by_reference"
)

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

    record = payments_utils.get_invoice(db, active_user, invoiceId)
    customer = {
        "name": active_user["name"],
        "email": active_user["email"],
    }

    flw_txref = "MC-" + str(round(time.time()) * 1000)
    user_payload = build_payment_payload(
        flw_txref, float(record.price), customer
    )

    response = get_rave_link(user_payload)
    pay_link = response["data"]["link"]
    our_ref_id = "REF-" + str(round(time.time()))
    serialized_data = serialize_to_db(
        our_ref_id, flw_txref, pay_link, record
    )

    db_crud.save(db, db_models.Payments, serialized_data)
    return {
        "flw_txref": flw_txref,
        "status": response["status"],
        "link": response["data"]["link"],
        "link_type": response["message"],
    }


@router.get(
    "/verifyPayments",
    summary="Verify's if the users payment was successful",
    description="This endpoint is automatically called by payment processor"
    " after user completes payment process. We then verify the"
    " the users payments if it was successful or cancelled",
)
async def callback(
    req_url: Request,
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """Verify's user payments"""

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint still in development",
    )

    query_params = str(req_url.query_params)
    params = dict(item.split("=") for item in query_params.split("&"))

    print(params)

    # status can be cancelled, failed,
    if params.get("status") == "cancelled":
        # update record with txref to cancelled
        print("cancelled")

    url = r.url

    # return params


# failed response
failed_rsp = {
    "params": {
        "status": "cancelled",
        "tx_ref": "REF-1697999408.2708738",
    },
    "url": {
        "_url": "http://localhost:5000/callback?status=cancelled&tx_ref=REF-1697999408.2708738",
    },
}


def get_rave_link(user_payload):
    """makes the network call to flutterwave api"""

    try:
        response = req.post(
            CHECKOUT_ENDPOINT,
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
        #"redirect_url": "http://localhost:5000/raveCheckout/verifyPayments",
        "redirect_url": "https://japaconsults.sammykingx.tech/raveCheckout/verifyPayments"
        "customizations": {
            "title": "sammykingx-japaconsults",
            "logo": "https://japaconsults.com/wp-content/"
            "uploads/2021/05/LogoMakr-6zrJ19.png",
        },
    }

    return payload


def serialize_to_db(ref_id, flw_txref, pay_link, record):
    """serialize the user data to db format"""

    # live mode
    flw_ref = pay_link.removeprefix(
        "https://checkout.flutterwave.com/v3/hosted/pay/"
    )

    # test mode
    # flw_ref = pay_link.split("/hosted/pay/")[-1]

    return {
        "ref_id": ref_id,
        "flw_ref": flw_ref,
        "flw_txRef": flw_txref,
        "inv_id": record.inv_id,
        "amount": record.price,
        "payer_email": record.to_email,
        "payment_type": "rave modal",
    }
