from pydantic import BaseModel


class CardPayments(BaseModel):
    cardno: str
    expirymonth: str
    expiryyear: str
    cvv: str
    amount: float
    pin: str

    class Config:
        json_schema_extra = {
                "example": {
                        "cardno": "234567890987654",
                        "expirymonth": "12",
                        "expiryyear": "34",
                        "cvv": "324",
                        "amount": 2400.89,
                        "pin": "2345"
                    }
            }
