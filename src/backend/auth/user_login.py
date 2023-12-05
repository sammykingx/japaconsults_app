from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    status,
)
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import db_crud, db_engine, db_models, redis_db, schema
from utils import email_notification, password_hash, redis_user_token
from auth import oauth2_users
from typing import Annotated
from dotenv import load_dotenv
from pydantic import BaseModel, EmailStr
from docs.auth import (
    generate_email_token,
    verify_email,
    password_change,
    logout,
)
from . import auth_schema
import datetime, jwt, pathlib, os


router = APIRouter(prefix="/auth", tags=["Authentication"])

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
)

def validate_email_token(token: str) -> dict:
    """checks if the email token received is still valid"""

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


@router.post(
    "/",
    summary="Exchange user credentials for access token",
    description="Generates access token for verified users",
    response_model=auth_schema.TokenResponse,
)
async def authenticate_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """authenticates a user based on details sent and returns a token"""

    user = db_crud.get_specific_record(
        db, db_models.User, email=form_data.username
    )

    if not user:
        raise CREDENTIALS_EXCEPTION

    if not password_hash.verify_pwd(form_data.password, user.password):
        raise CREDENTIALS_EXCEPTION

    # update last login
    user.last_login = datetime.datetime.utcnow()
    db.commit()
    db.refresh(user)

    token = oauth2_users.create_token(user)

    return {"access_token": token, "token_type": "Bearer"}


@router.post(
    "/generate/emailToken",
    summary="Generates email verification token to verify email",
    description="Use this endpoint to generate tokens for forget "
    "password as well as email verification",
    response_model=auth_schema.ResponseToken,
    responses=generate_email_token.response_codes,
)
async def generate_email_token(
    mail: EmailStr,
    verv_type: auth_schema.TokenType,
    req: Request,
    bg_task: BackgroundTasks,
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """generate email verification token to email address"""

    redis = redis_db.redis_factory()
    key = mail + ":email_token"

    #if redis.exists(key):
    #    raise HTTPException(
    #        status_code=status.HTTP_400_BAD_REQUEST,
    #        detail="User already has an active validation token",
    #    )

    user = db_crud.get_specific_record(db, db_models.User, email=mail)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user account found",
        )

    email_token = oauth2_users.email_verification_token(mail)
    redis_user_token.add_email_token(key, email_token)

    # verv_endpoint = "{}{}{}".format(
    #    req.url_for("verify_user_email"), "?token=", email_token
    # )

    templates = Jinja2Templates(directory="templates")
    if verv_type == auth_schema.TokenType.new_user:
        message = templates.TemplateResponse(
            "email_verification.html",
            {
                "user": f"{user.first_name} {user.last_name}",
                "email_token": email_token,
                "request": req,
            },
        ).body.decode()

        # email_notification.send_email(
        #    message, mail, "Account Verification Required"
        # )

        bg_task.add_task(
            email_notification.send_email,
            message,
            mail,
            "Account Verification Required",
        )

    else:
        message = templates.TemplateResponse(
            "changePassword.html",
            {
                "user": f"{user.first_name} {user.last_name}",
                "email_token": email_token,
                "request": req,
            },
        ).body.decode()

        # email_notification.send_email(
        #    message, mail, "IT'S URGENT - Verify password change"
        # )

        bg_task.add_task(
            email_notification.send_email,
            message,
            mail,
            "IT'S URGENT - Verify password change",
        )
    
    return {"token": email_token}


@router.get(
    "/verifyEmail",
    summary="verify user email",
    description="Verify's the user email encoded in token",
    responses=verify_email.response_codes,
    response_model=auth_schema.SuccessfullEmailVerification,
)
async def verify_user_email(
    token: str, db: Annotated[Session, Depends(db_engine.get_db)]
):
    """verify"s the user email address provided and updates user
    verification status to True
    """

    encoded_data = validate_email_token(token)
    key = encoded_data["email"] + ":email_token"
    redis = redis_db.redis_factory()
    if not redis.exists(key):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already Verified",
        )

    user = db_crud.get_specific_record(
        db, db_models.User, email=encoded_data["email"]
    )

    # if user.is_verified:
    #    raise HTTPException(
    #        status_code=status.HTTP_409_CONFLICT,
    #        detail="User already Verified",
    #    )

    user.is_verified = True

    try:
        db.commit()
        db.refresh(user)

    except Exception as err:
        print(f"err on saving new details => {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server encountered some issues during verification, "
            "check back later or contact administrator",
        )

    redis.delete(key)
    return {
        "msg": "User account verified",
        "name": f"{user.first_name} {user.last_name}",
        "email": user.email,
        "is_verified": user.is_verified,
    }


# class ChangePassword(BaseModel):
#    token: str
#    new_pwd: str


@router.patch(
    "/changePassword",
    summary="Changes the user password",
    responses=password_change.response_codes,
)
async def change_user_password(
    payload: auth_schema.ChangePassword,
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """Updates the user password"""

    encoded_data = validate_email_token(payload.token)
    key = encoded_data["email"] + ":email_token"
    redis = redis_db.redis_factory()

    if not redis.exists(key):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passowrd already changed",
        )

    user = db_crud.get_specific_record(
        db, db_models.User, email=encoded_data["email"]
    )

    user.password = password_hash.hash_pwd(payload.new_pwd)

    try:
        db.commit()
        db.refresh(user)

    except Exception as err:
        print(f"Error while changing users pwd: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server encountered some issues, check back later",
        )

    redis.delete(key)
    return {"msg": "succesful"}


@router.get(
    "/logout",
    summary="Invalidates the user token",
    responses=logout.response_codes,
)
async def logout_user(token: str = Depends(oauth2_users.oauth2_scheme)):
    """revokes the user token"""

    oauth2_users.revoke_token(token)

    return {"msg": "logout succesful"}
