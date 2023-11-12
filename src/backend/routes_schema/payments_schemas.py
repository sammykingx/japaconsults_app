from pydantic import BaseModel, EmailStr
from datetime import date, datetime


class PendingPayments(BaseModel):
    ref_id: str
    rave_txRef: str
    invoice_id: str
    title:  str | None
    amount: float
    paid: bool = False
    status: str | None
    paid_by: str | None
    payer_email: EmailStr | str
    payment_type: str


class PaymentResponse(PendingPayments, BaseModel):
    #paid_by: str | None
    #amount: float
    paid_at: datetime | None
    #payment_type: str


class UserTotalSpend(BaseModel):
    name: str
    email: EmailStr
    total_spend: float
