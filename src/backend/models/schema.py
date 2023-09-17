from pydantic import BaseModel, EmailStr
from typing import Dict, List
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
    user_id: int
    content: str
    publish: bool = False
    doc_url: List[str] | None = None
    date_created: datetime

    class Config:
        orm_mode = True


class SendMessage(BaseModel):
    msg: str
    from_id: int
    to_id: int
    docs: List[str] | None
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
