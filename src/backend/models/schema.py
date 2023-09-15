from pydantic import BaseModel


class RegisterUser(BaseModel):
    name: str
    email: str
    password: str
    phone_num: int
    role: str

    class Config:
        orm_mode = True


class Drafts(BaseModel):
    uid: int
    content: str
    publish: bool
    doc_url: list

    class Config:
        orm_mode = True


class SendMessages(BaseModel):
    msg: str
    from_id: int
    to_id: int
    time_stamp: str
    doc: list

    class Config:
        orm_mode = True


class CreateInvoice(BaseModel):
    from_uid: int
    to_uid: int
    paid: bool = False

    class Config:
        orm_mode = True
