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
                "cardno": "234567890987654",
                "expirymonth": "12",
                "expiryyear": "34",
                "cvv": "324",
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


class BankTransferResponse(BaseModel):
    ref_id: str
    bank_name: str
    bank_account: str
    expires_in: int
    message: str


class VerifyBankTransfer(BaseModel):
    msg: str
    transactionComplete: bool
