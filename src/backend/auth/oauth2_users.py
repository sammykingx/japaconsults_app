from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt, os


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth")

# change the details to invalid token
token_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED, detail="token verification error"
)

REVOKED_TOKENS = []

load_dotenv()


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


def verify_token(token: str = Depends(oauth2_scheme)) -> dict:
    """verify token integrity and returns the user data encoded in token"""

    if token in REVOKED_TOKENS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User token")
    try:
        data = jwt.decode(token, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM"))

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )

    except Exception as err:
        raise token_exception

    return data


def revoke_token(token: str = Depends(oauth2_scheme)) -> None:
    """revokes user token"""

    if token in REVOKED_TOKENS:
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid User Token"
        )

    REVOKED_TOKENS.append(token)
    print(f"Revoked tokens: {REVOKED_TOKENS}")
