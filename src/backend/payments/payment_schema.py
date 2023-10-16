from pydantic import BaseModel


class CardPayments(BaseModel):
    cardno: int
    cvv: int
    expirymonth: int
    expiryyear: int
    amount: float
    phonenumber: int
