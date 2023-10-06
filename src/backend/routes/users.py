from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import db_engine, db_crud, db_models, schema
from typing import Dict, List
from auth import oauth2_users
from utils import email_notification, password_hash, verify_number
from typing import Annotated
from pydantic import BaseModel, EmailStr
import jwt


router = APIRouter(prefix="/user", tags=["User"])


USER_ROLES = ("user", "manager", "staff")


def users_to_dict(user: db_models.User) -> dict:
    """builds the user_json object"""

    data = {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "phone_num": user.phone_num,
        "role": user.role,
        "is_verified": user.is_verified,
    }
    return data


def dict_user_data(uid: int, db: Session) -> dict:
    """takes a user record and returns an object of the user details"""

    user = db.query(db_models.User).filter(db_models.User.user_id == uid).first()

    if not user:
        raise HTTPException(status_code=404, detail="no data found")

    profile = users_to_dict(user)

    profile_data = {
        # "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "phone_num": user.phone_num,
        "role": user.role,
    }

    return profile


# temp
class AllUsersResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    phone_num: str
    role: str
    is_verified: bool


@router.get(
    "/",
    summary="Gets all users from the database",
    description="This method is to be used by the manager not staffs or users.",
)
async def get_users(
    user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
) -> List[Dict[str, str | int]]:
    """gets all users in the user table"""

    if user["role"] != "manager":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="User Not allowed"
        )

    users = db_crud.get_all(db, db_models.User)

    if not users:
        return HTTPException(status_code=404, detail="no users in db")

    all_users = []
    for user in users:
        if user.role != "manager":
            user_record = users_to_dict(user)
            all_users.append(user_record)

    return all_users


# temp
class ProfileResponse(BaseModel):
    name: str
    email: EmailStr
    phone_num: str
    role: str


@router.get(
    "/profile",
    summary="Gets the current user profile details",
    response_model=ProfileResponse,
)
async def user_profile(
    token: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
) -> dict:
    """return the users details"""

    user_id = token["sub"]
    profile = dict_user_data(user_id, db)
    return profile


# temp
class UserRegistrationToken(BaseModel):
    details: str
    status: str = "Unverified"
    token: str


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="creates a user in the database",
    response_model=UserRegistrationToken,
)
async def register_user(
    payload: schema.RegisterUser, db: Annotated[Session, Depends(db_engine.get_db)]
):
    """Adds a user to the database"""

    if payload.role not in USER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid user role"
        )
    if not verify_number.verify_phone_num(payload.phone_num):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Phone number format",
        )

    resp = (
        db.query(db_models.User).filter(db_models.User.email == payload.email).first()
    )

    if resp:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="email account exist"
        )

    temp_data = payload.dict().copy()
    temp_data["password"] = password_hash.hash_pwd(temp_data["password"])
    db_crud.save(db, db_models.User, temp_data)
    token = oauth2_users.email_verification_token(payload.email)
    message = "Welcome to japaconsults user Portal, click the link to verify email"
    email_notification.send_email(message, temp_data["email"], "WELCOME EMAIL")
    return {
        "details": "user account created succefully",
        "status": "Unverified",
        "token": token,
    }


@router.put("/change_role", summary="Updates the user profile")
async def change_user_role(
    payload: schema.ChangeUserRole,
    user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """Updates the existing record of the user to the infomation
    provided on the payload
    """

    if user["role"] != "manager":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized"
        )

    if payload.role not in ("staff", "user"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user role"
        )

    try:
        user = db.query(db_models.User).filter_by(email=payload.user_email).first()

    except Exception as err:
        # send mail
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="oopsy !! could not execute this, try in 2hrs time",
        )
    if not user:
        raise HTTPexception(
            status_code=status.HTTP_404_NOT_FOUND, detail="No user found"
        )

    user.role = payload.role
    db.commit()
    db.refresh(user)
    user_data = {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "role": payload.role,
    }
    return {"details": "role updated", "data": user_data}
