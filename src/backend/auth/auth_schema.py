from pydantic import BaseModel, EmailStr
from enum import Enum

class TokenResponse(BaseModel):
    """the token response when user exchange credentials for token"""
 
    access_token: str
    token_type: str


class ResponseToken(BaseModel):
    """the response when user generate token for email or password change"""

    token: str

    class Config:
        json_schema_extra = {
                "example": {
                    "token": "asgfdhhfi9rur9uw.jjhhhfghw8w.uturtwuu",
                },
            }


class TokenType(Enum):
    """Used to specify the available options in the generate email token"""

    new_user = "new_user"
    password_change = "password_change"


class ChangePassword(BaseModel):
    """the expected body param when user needs to change password"""

    token: str
    new_pwd: str

    class Config:
        json_schema_extra = {
            "example": {
                "token": "asgfdhhfi9rur9uw.jjhhhfghw8w.uturtwuu",
                "new_pwd": "123swed4!67",
            },
        }


class SuccessfullEmailVerification(BaseModel):
    """the response returned when a user succesfully verifies email"""

    msg: str
    name: str
    email: EmailStr
    is_verified: bool
