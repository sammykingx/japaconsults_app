from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_crud, db_models, schema
from datetime import date, datetime
from typing import Annotated
import time

router = APIRouter(
    prefix="/invoice",
    tags=["Invoice"],
    responses={
        200: {"description": "Successful response"},
        201: {"description": "Invoice created"},
        400: {"description": "Missing required data to process request"},
        401: {"description": "Unauthorized access to resource"},
        403: {"description": "Cannot access resource"},
        404: {"description": "Resource Not Found"},
        500: {"description": "Internal server error"},
    },
)


@router.post(
    "/create",
    summary="Creates invoice",
    description="Creates invoice, should not be used by 'user' roles",
    status_code=status.HTTP_201_CREATED,
)
async def create_invoice(
    payload: schema.CreateInvoice,
    active_user: Annotated[dict, Depends(oauth2_userd.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """creates invoice"""

    if active_user == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access to resource",
        )
    check_payload(payload)
    data = payload.model_dump()
    data.update(
        {
            "inv_id": "JPC-" + str(round(time.time())),
            "created_at": datetime.utcnow(),
            "created_by": active_user["name"],
        }
    )
    db_crud.save(db, db_models.Invoices, data)
    if data.get("to_email", None):
        # send user an email for new invoice
        pass

    return {"msg": "Invoice created", "invoiceId": data["inv_id"]}


def check_payload(payload: schema.CreateInvoice) -> None:
    """checks the user payload"""

    if len(payload.title) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="number of characters in 'title' greater than 50",
        )
    if len(payload.desc) > 250:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="number of characters is greater than 100",
        )
    price = str(payload.price)
    if len(price.split(".")[1]) > 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Number of digits of decimal must be less than 2",
        )
