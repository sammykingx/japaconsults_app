from pydantic import BaseModel, Field
from typing import Annotated


class CardPayments(BaseModel):
    cardno: Annotated[str, Field(strict=True)]
    expirymonth: Annotated[str, Field(strict=True, max_length=2)]
    expiryyear: Annotated[str, Field(strict=True, max_length=2)]
    cvv: Annotated[str, Field(strict=True, max_length=3)]
    pin: Annotated[str, Field(strict=True, max_length=4)]

    class Config:
        json_schema_extra = {
            "example": {
                "cardno": "5399838383838381",
                "expirymonth": "09",
                "expiryyear": "32",
                "cvv": "564",
                "pin": "2345",
            }
        }


class CardResponse(BaseModel):
    ref_id: str
    validationRequired: bool

    class Config:
        json_schema_extra = {
            "example": {
                "ref_id": "REF-12345678903",
                "validationRequired": False,
            }
        }


class VerifyCardPayments(BaseModel):
    ref_id: str
    otp: Annotated[str, Field(strict=True, max_length=8)]

    class Config:
        json_schema_extra = {
            "example": {
                "ref_id": "REF-1223455677890",
                "otp": "123456",
            }
        }


class SuccessfullCardPayments(BaseModel):
    transactionComplete: bool
    ref_id: str
    inv_id: str
    amount: float
    chargedamount: float
    currency: str


class BankTransferResponse(BaseModel):
    ref_id: str
    bank_name: str
    bank_account: str
    expires_in: int
    message: str


class VerifyBankTransfer(BaseModel):
    msg: str
    transactionComplete: bool


class RaveCheckoutResponse(BaseModel):
    ref_id: str
    status: str
    link: str
    link_type: str


class RaveVerifyPayments(BaseModel):
    status: str
    msg: str


class CallbackResponse(BaseModel):
    status: str
    ref_id: str
