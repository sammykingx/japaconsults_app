from pydantic import BaseModel, EmailStr
from datetime import datetime


class RegisterUser(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone_num: str = "+2347043215534"
    role: str = "user"

    class Config:
        orm_mode = True


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
    # doc_url: list
    last_updated: datetime


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
