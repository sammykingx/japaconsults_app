from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.schema import RegisterUser
from models.db_engine import get_db
from models import db_models
from models import db_crud
from typing import Dict, List


router = APIRouter(prefix="/user", tags=["User"])

all_user = {
    1: {"name": "John doe", "email": "me@me.com", "role": "user"},
    2: {"name": "james smith", "email": "james@me.com", "role": "manager"},
    3: {"name": "sammy kingx", "email": "sammy@me.com", "role": "admin"},
}


@router.get("/")
async def get_users(db: Session = Depends(get_db)) -> List[Dict[str, str | int]]:
    """gets a list of all users in the user table"""
    users = db_crud.get_all(db, db_models.User)
    all_users = []
    if users:
        for user in users:
            user_record = {"user_id": user.user_id, "email": user.email, "role": user.role}
            all_users.append(user_record)
    return all_users if all_users else {"error": "no user in db"}


@router.get("/{uid}")
async def get_user_by_id(uid: int, db: Session = Depends(get_db)):
    """gets a user details by desired specification

    @uid: The id of the user
    @user_email: email of the user
    @user_role: the role/ account type
    """
    #data = all_user.get(user_id, None)

    #user = db.query(db_models.User).filter(db_models.User.user_id==uid).first()

    
    resp = db_crud.get_by(db, db_models.User, user_id=uid)

    return resp if resp else {"error": "no user data"}


@router.post("/register")
async def reg_user(payload: RegisterUser, db: Session = Depends(get_db)):
    """Adds a user to the database
    check if exception occurs too, taking too long to create etc.
    """

    #user = db_models.User(**payload.dict())
    #db.add(user)
    #db.commit()
    #db.refresh(user)

    # user_id = len(all_user) + 1
    # all_user.update({user_id: payload.dict()})

    db_crud.save(db, db_models.User, payload)
    data = db_crud.get_by(db, db_models.User, email=payload.email)
    return {"response": "account created", "details": data}
