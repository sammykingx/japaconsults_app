from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import db_engine, db_models, schema
from utils import password_hash
from auth import oauth2_users
from typing import Annotated
from google_auth_oauthlib.flow import Flow
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr
import jwt, pathlib, os


router = APIRouter(prefix="/auth", tags=["Auth"])

credentials_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
)

GOOGLE_CLIENT_ID = (
    "575832262735-pimi2lkkerr3rt9h10rc2c02o0q6q9sa.apps.googleusercontent.com"
)
GOOGLE_CLIENT_SECRET = "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"
REDIRECT_URL = "http://localhost:5000/Oauth/google/callback"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

flow = Flow.from_client_secrets_file(
    client_secrets_file=os.path.join(pathlib.Path(__file__).parent, "ls_OauthID.json"),
    scopes=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
    redirect_uri=REDIRECT_URL,
)

client_state = []

INVALID_EMAIL_TOKEN = []


def validate_email_token(token: str):
    """checks if the email token received is still valid"""

    if token in INVALID_EMAIL_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid user token"
        )
    load_dotenv()
    try:
        encoded_data = jwt.decode(
            token, os.getenv("SECRET_KEY"), os.getenv("ALGORITHM")
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="expired verification token",
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request credentials",
        )
    return encoded_data


@router.post("/", response_model=schema.TokenResponse)
async def authenticate_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """authenticates a user based on details sent and returns a token"""

    user = (
        db.query(db_models.User)
        .filter(db_models.User.email == form_data.username)
        .first()
    )

    if not user:
        raise credentials_exception

    if not password_hash.verify_pwd(form_data.password, user.password):
        raise credentials_exception

    token = oauth2_users.create_token(user)

    return {"access_token": token, "token_type": "Bearer"}

# temp
class SendMailToken(BaseModel):
    email: EmailStr


@router.post(
    "/send/emailToken",
    summary="Sends email validation token to verify email",
    description="Use this endpoint to generate tokens for forget password as well as email verification",
)
async def send_email_token(
    mail: EmailStr, db: Annotated[Session, Depends(db_engine.get_db)]
):
    """sends email verification token to email address"""

    try:
        user = db.query(db_models.User).filter_by(email=mail).first()
    except Exception:
        raise HTTPExceotion(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server encountered some issues, check back later",
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No account found"
        )
    # token =
    return {"token": oauth2_users.email_verification_token(mail)}


# temp
class VerifyEmail(BaseModel):
    token: str


@router.post(
    "/verify_email",
    summary="verify user email",
    description="Verify's the user email provided",
)
async def verify_user_email(
    payload: VerifyEmail, db: Annotated[Session, Depends(db_engine.get_db)]
):
    """verify"s the user email address provided and updates user
    verification status to True
    """

    encoded_data = validate_email_token(payload.token)
    try:
        user = db.query(db_models.User).filter_by(email=encoded_data["email"]).first()

        user.is_verified = True
        db.commit()
        db.refresh(user)

    except Exception:
        raise HTTPExceotion(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server encountered some issues, check back later",
        )
    INVALID_EMAIL_TOKEN.append(token.token)
    return {
        "details": "User account verified",
        "name": user.name,
        "is_verified": user.is_verified,
    }


class ChangePassword(BaseModel):
    token: str
    new_pwd: str


@router.post("/changePassword", summary="Changes the user password")
async def change_user_password(
    payload: ChangePassword, db: Annotated[Session, Depends(db_engine.get_db)]
):
    """Updates the user password"""

    encoded_data = validate_email_token(payload.token)
    try:
        user = db.query(db_models.User).filter_by(email=encoded_data["email"]).first()
        user.password = password_hash.hash_pwd(payload.new_pwd)
        db.commit()
        db.refresh(user)

    except Exception as err:
        raise HTTPExceotion(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server encountered some issues, check back later",
        )
    INVALID_EMAIL_TOKEN.append(payload.token)
    return {"status": "succesful"}


@router.post("/logout", summary="Invalidates the user token")
async def logout_user(token: str = Depends(oauth2_users.oauth2_scheme)):
    """revokes the user token"""

    oauth2_users.revoke_token(token)
    return {"details": "logout succesful"}


@router.post("/google/me", include_in_schema=False)
async def authenticate_with_google():
    """authenticates a user with google"""

    auth_url, state = flow.authorization_url()
    client_state.append(state)
    return RedirectResponse(auth_url)


@router.get("/Oauth/google/callback", include_in_schema=False)
async def google_callback(req: Request):
    if req.query_params.get["state"] not in client_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detai="Invalid Request from client"
        )
    flow.fetch_token(authorization_response=req.url)
    credentials = flow.credentials
    user_info = jwt.decode(credentials.id_token, options={"verify_signature": False})
    print(user_info)
    return {"details": "not fully implemeted yet"}
