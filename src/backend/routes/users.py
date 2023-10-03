from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import db_crud, db_models, schema
from models.db_engine import get_db
from typing import Dict, List
from auth import oauth2_users
from utils import password_hash, email_notification


router = APIRouter(prefix="/user", tags=["User"])


def users_to_dict(user: db_models.User) -> dict:
    """builds the user_json object"""

    data = {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "phone_num": user.phone_num,
        "role": user.role,
    }
    return data


def dict_user_data(uid: int, db: Session) -> dict:
    """takes a user record and returns an object of the user details"""

    user = db.query(db_models.User).filter(db_models.User.user_id == uid).first()

    if not user:
        raise HTTPException(status_code=404, detail="no data found")

    profile = users_to_dict(user)
    
    profile_data = {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "phone_num": user.phone_num,
        "role": user.role,
    }

    return profile


@router.get("/",
        summary="Gets all users from the database")
async def get_users(
    user: dict = Depends(oauth2_users.verify_token), db: Session = Depends(get_db)
) -> List[Dict[str, str | int]]:
    """gets all users in the user table"""

    if user["role"] != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User Not allowed")

    users = db_crud.get_all(db, db_models.User)

    if not users:
        return HTTPException(status_code=404, detail="no users in db")

    all_users = []
    for user in users:
        if user.role == "user":
            user_record = users_to_dict(user)
            all_users.append(user_record)

    return all_users


@router.get("/profile")
async def user_profile(
    token: dict = Depends(oauth2_users.verify_token), db: Session = Depends(get_db)
) -> dict:
    """return the users details"""

    user_id = token["sub"]
    profile = dict_user_data(user_id, db)
    return profile


@router.post( "/register", status_code=status.HTTP_201_CREATED)
async def reg_user(payload: schema.RegisterUser, db: Session = Depends(get_db)):
    """Adds a user to the database"""

    user_roles = ("user", "manager", "staff")
    if payload.role not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="invalid user role"
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
    message = "Welcome to japaconsults user Portal"
    email_notification.send_email(message, temp_data["email"], "WELCOME EMAIL")
    return {"details": "user account created succefully"}
