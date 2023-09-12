from pydantic import BaseModel


class RegisterUser(BaseModel):
    name: str
    email: str
    password: str
    phone_num: int
    role: str

    class Config:
        orm_mode = True
