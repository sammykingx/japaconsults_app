from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_crud, db_models
from online_payments import payments_utils
from dotenv import load_dotenv
from typing import Annotated
import requests as req
import os, time


app  = APIRouter(
        prefix="/raveCheckout",
        tags=["Flutterwave Checkout"],
        responses={
            500: {"description": "Internal server error",}
        },
)

CHECKOUT_ENDPOINT = "https://api.flutterwave.com/v3/payments"

@app.get(
        "/pay",
        summary="Creates payments link users use in processing payments.",
        description="The invoice ID should be passed as query parameter"
                    "and then a checkout url is generated for user payment."
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

    tx_ref = "REF-" + str(round(time.time()))
    payload = {
            "tx_ref": tx_ref,
            "amount": amount,
            "customer": customer,
            "redirect_url": "http://localhost:5000/callback",
            "customizations": {
                "title": "sammykingx-japaconsults",
                "logo": "https://japaconsults.com/wp-content/uploads/2021/05/LogoMakr-6zrJ19.png"
            },
        }
    load_dotenv()
    header = {
        "Authorization": "Bearer {}".format(os.gentenv["RAVE_SECRET_KEY"]),
    }
    
    try:
        res = req.post(
                CHECKOUT_ENDPOINT,
                headers=header,
                json=payload,
                timeout=5,
            ).json()
    
    except req.exceptions.ConnectionError:
        raise HTTException(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                detail="ERROR: check internet connection",
            )

    except req.exceptions.ConnectTimeout:
        raise  HTTPException(
                status_code=408,
                detail="couldnt establish a connection, check internet provider"
            )

    except req.exceptions.ReadTimeout:
        raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="payment processor took too long to respond",
            )
    return res


@app.get("/callback")
async def callback(r: Request):
    """the call back to see all params"""
    params = r.query_params
    url = r.url

    return {"params": params, "url": url}

# failed response
failed_rsp = {
        "params":{
            "status":"cancelled",
            "tx_ref":"REF-1697999408.2708738",
        },
        
        "url":{
            "_url":"http://localhost:5000/callback?status=cancelled&tx_ref=REF-1697999408.2708738",
        }
}
