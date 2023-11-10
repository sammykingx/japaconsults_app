from pydantic import BaseModel, EmailStr
from datetime import datetime, date


class InvoiceResponse(BaseModel):
    inv_id: str
    title: str
    desc: str
    price: float
    to_email: EmailStr
    created_at: datetime
    created_by: str
    updated_at: datetime | None
    updated_by: str | None
    due_date: date
    paid: bool
    paid_at: datetime | None
    rave_txref: str | None
    ref_id: str | None


class UpdateInvoice(BaseModel):
    inv_id: str
    title: str
    desc: str
    price: float
    due_date: date

    class Config:
        json_schema_extra = {
            "example": {
                "inv_id": "JPC-1243567809",
                "title": "title of the invoice",
                "desc": "a short description of the invoice generated",
                "price": 2500.00,
                "due_date": "2024-12-30",
            }
        }
