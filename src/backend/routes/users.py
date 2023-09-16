from fastapi import APIRouter, Depends, HTTPException
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


def build_user_json(user: Dict) -> Dict[str, str | int]:
    pass


@router.get("/")
async def get_users(db: Session = Depends(get_db)) -> List[Dict[str, str | int]]:
    """gets a list of all users in the user table"""
    users = db_crud.get_all(db, db_models.User)
    if not resp:
        return HTTPException(status_code=404, detail="no users in db")
    all_users = []
    if users:
        for user in users:
            user_record = {
                "user_id": user.user_id,
                "name": user.name,
                "email": user.email,
                "phone_num": user.phone_num,
                "role": user.role,
            }
            all_users.append(user_record)
    return all_users


@router.get("/{uid}")
async def get_user_by_id(
    uid: int, db: Session = Depends(get_db)
) -> List[Dict[str, str | int]]:
    """gets a user details by desired specification

    @uid: The id of the user
    @user_email: email of the user
    @user_role: the role/ account type
    """
    # data = all_user.get(user_id, None)

    # user = db.query(db_models.User).filter(db_models.User.user_id==uid).first()

    resp = db_crud.get_by(db, db_models.User, user_id=uid)
    if not resp:
        raise HTTPException(status_code=404, detail="no data found")

    data = []
    for field in resp:
        temp = {
            "user_id": field.user_id,
            "name": field.name,
            "email": field.email,
            "phone_num": field.phone_num,
            "role": field.role,
        }
        data.append(temp)
    return data


@router.post("/register")
async def reg_user(payload: RegisterUser, db: Session = Depends(get_db)):
    """Adds a user to the database
    check if exception occurs too, taking too long to create etc.
    """

    # user = db_models.User(**payload.dict())
    # db.add(user)
    # db.commit()
    # db.refresh(user)

    # user_id = len(all_user) + 1
    # all_user.update({user_id: payload.dict()})

    # return json/dict not list, work on that later

    db_crud.save(db, db_models.User, payload)
    resp = db_crud.get_by(db, db_models.User, email=payload.email)
    if not resp:
        raise HTTPException(status_code=400, detail="account exist")

    data = {}
    for field in resp:
        temp = {
            "user_id": field.user_id,
            "name": field.name,
            "email": field.email,
            "phone_num": field.phone_num,
            "role": field.role,
        }
        data.update(temp)

    return {"response": "account created", "details": data}
