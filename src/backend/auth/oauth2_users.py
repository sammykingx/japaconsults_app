from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from models import db_engine
from typing import Annotated
from sqlalchemy.orm import Session
import jwt, os


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

# change the details to invalid token
token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="token verification error"
)

REVOKED_TOKENS = []

load_dotenv()


def is_user_verified(mail: EmailStr):
    """checks if the user email is verified"""

    try:
        user = db.query(db_models.User).filter_by(email=mail).first()

    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server encountered some issues, check back later",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, details="email not verified"
        )
    return True


def email_verification_token(email: EmailStr) -> str:
    """Builds an email verification token for users"""

    user_data = {
        "email": email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }
    token = jwt.encode(user_data, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM"))
    return token


def token_payload(user) -> dict:
    """builds the payload to encode in token"""

    payload = {
        "sub": user.user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }
    return payload


def create_token(user) -> str:
    """creates an oauth2 token for the specified user"""

    data = token_payload(user)
    dup_data = data.copy()
    iat = datetime.utcnow()
    exp = datetime.utcnow() + timedelta(minutes=30)
    dup_data.update({"iat": iat, "exp": exp})

    token = jwt.encode(dup_data, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM"))
    return token


def verify_token(token: Annotated[str, Depends(oauth2_scheme)]) -> dict:
    """verify token integrity and returns the user data encoded in token"""

    if token in REVOKED_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User token"
        )
    try:
        data = jwt.decode(token, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM"))

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )

    except Exception as err:
        raise token_exception
#    is_user_verified(data["email"])
    return data


def revoke_token(token: str = Depends(oauth2_scheme)) -> None:
    """revokes user token"""

    if token in REVOKED_TOKENS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User Token"
        )

    REVOKED_TOKENS.append(token)
    # print(f"Revoked tokens: {REVOKED_TOKENS}")
