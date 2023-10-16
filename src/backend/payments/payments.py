from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_crud, db_models
from typing import Annotated
from flutterwave import rave_pay
import payment_schema


router = APIRouter(
        prefix="/payments",
        tags=["Payments"],
        responses={
            200: {"description": "Successfule Request"},
        }
    )

@router.get(
        "/card",
        summary="For card payments only",
        description="Should be used for processing card payments")
async def card_payments(
        payload: payment_schema.CardPayments,
        user: Annotated[dict, Depends(oauth2_users.verify_token)]
    ):
    """collect card payments"""

    pass
