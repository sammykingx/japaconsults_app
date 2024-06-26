from pydantic import BaseModel, EmailStr
from datetime import date, datetime


class PendingPayments(BaseModel):
    ref_id: str
    rave_txRef: str | None
    invoice_id: str
    title: str | None
    amount: float
    paid: bool = False
    status: str | None
    paid_by: str | None
    payer_email: EmailStr | str
    checkout_type: str | None


class PaymentResponse(PendingPayments, BaseModel):
    # paid_by: str | None
    # amount: float
    paid_at: datetime | None
    paid_amount: float | None
    payment_type: str | None


class UserTotalSpend(BaseModel):
    name: str
    email: EmailStr
    total_spend: float


class CancellTransactionResponse(BaseModel):
    ref_id: str
    inv_id: str
    status: str
    amount: float
    paid: bool
    checkout_type: str
