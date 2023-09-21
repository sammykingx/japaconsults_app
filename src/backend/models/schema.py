from pydantic import BaseModel, EmailStr
from datetime import datetime


class RegisterUser(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone_num: str | None
    role: str = "user"

    class Config:
        orm_mode = True


class CreateDrafts(BaseModel):
    content: str
    publish: bool = False
    doc_url: list | None = None
    date_created: datetime
    last_updated: datetime | None = None


class UpdateDrafts(CreateDrafts, BaseModel):
    draft_id: int

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
