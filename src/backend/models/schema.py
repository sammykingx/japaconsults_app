from pydantic import ConfigDict, BaseModel, EmailStr
from datetime import date, datetime


class RegisterUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    email: EmailStr
    password: str
    phone_num: str = "+2347043215534"
    role: str = "user"


class UserProfile:
    user_id: int
    name: str
    email: EmailStr
    phone_num: str = "+23408078907654"
    role: str = "user"


class ChangeUserRole(BaseModel):
    user_email: EmailStr
    role: str


class CreateDrafts(BaseModel):
    title: str
    content: str
    # doc_url: list | None = None
    date_created: datetime


class UpdateDrafts(BaseModel):
    draft_id: int
    title: str
    content: str
    last_updated: datetime


class CreateInvoice(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    title = str
    desc: str
    price: float
    to_email: EmailStr | None
    due_date: date

    class Config:
        json_schema_extra = {
                "example": {
                    "title" : "the invoice title",
                    "desc": "A short description of the invoice",
                    "price": 2500.00,
                    "to_email": "example@example.com",
                    "due_date": "date object",
                }
            }


class SendMessage(BaseModel):
    msg: str
    from_id: int
    to_id: int
    docs: list | None
    sent_time: datetime


class UpdateUserInfo(BaseModel):
    user_id: int
    phone_num: str | None = None
    profile_pic: str | None


class UpdateDraft(BaseModel):
    daft_id: int
    user_id: int
    publish: bool = False
    doc_url: dict | None
    last_updated: datetime


class LoginUser(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: int
    name: str
    role: str
