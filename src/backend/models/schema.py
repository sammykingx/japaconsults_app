from pydantic import ConfigDict, BaseModel, EmailStr
from datetime import date, datetime


class RegisterUser(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    phone_num: str
    role: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "first_name": "Test",
                "last_name": "user",
                "email": "testuser@gmail.com",
                "password": "yoursuperStrong!paswword",
                "phone_num": "+2348012334554",
                "role": "user",
            }
        }


class UserProfile:
    user_id: int
    name: str
    email: EmailStr
    phone_num: str
    role: str

    class Config:
        json_schema_extra = {
                "example": {
                    "user_id": 34,
                    "name": "sammykingx admin",
                    "email": "youremail@gmail.com",
                    "phone_num": "+2348091234567",
                    "role": "staff",}
            }


class ChangeUserRole(BaseModel):
    user_email: EmailStr
    role: str


class CreateDrafts(BaseModel):
    title: str
    content: str
    # doc_url: list | None = None
    # date_created: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "title": "The title of the note",
                "content": "The content of the notes. It can be long as possible",
            }
        }


class UpdateDrafts(BaseModel):
    draft_id: int
    title: str
    content: str
    # last_updated: datetime


class CreateInvoice(BaseModel):
    title: str
    desc: str
    price: float
    to_email: EmailStr | None
    due_date: date

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "title": "the invoice title",
                "desc": "A short description of the invoice",
                "price": 2500.12,
                "to_email": "user@example.com",
                "due_date": "2024-12-31",
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
    phone_num: str | None
    profile_pic: str | None


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
