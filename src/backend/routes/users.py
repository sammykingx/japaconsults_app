from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import db_crud, db_models, schema
from models.db_engine import get_db
from typing import Dict, List
from auth import oauth2_users
from utils import password_hash


router = APIRouter(prefix="/user", tags=["User"])

all_user = {
    1: {"name": "John doe", "email": "me@me.com", "role": "user"},
    2: {"name": "james smith", "email": "james@me.com", "role": "manager"},
    3: {"name": "sammy kingx", "email": "sammy@me.com", "role": "admin"},
}


@router.get("/")
async def get_users(
    user: str = Depends(oauth2_users.verify_token),
    db: Session = Depends(get_db),
    uid: int | None = None
) -> List[Dict[str, str | int]]:
    """gets users in the user table

    When no query is passed to the handler it gets all the users in the database.
    when you pass a valid user_id, the user data is returned.
    """

    if user["role"] != "manager":
        raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed")

    if uid:
        #resp = db_crud.get_by(db, db_models.User, user_id=uid)
        resp = db.query(db_models.User).filter(db_models.User.user_id == uid).first()
        if not resp:
            raise HTTPException(status_code=404, detail="no data found")

        data = {
                "user_id": resp.user_id,
                "name": resp.name,
                "email": resp.email,
                "phone_num": resp.phone_num,
                "role": resp.role,
        }
        return [data]

    users = db_crud.get_all(db, db_models.User)

    if not users:
        return HTTPException(status_code=404, detail="no users in db")

    all_users = []
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


# @router.get("/{uid}")
# async def get_user_by_id(
#    uid: int, db: Session = Depends(get_db)
# ) -> List[Dict[str, str | int]]:
#    """gets a user details by desired specification
#
#    @uid: The id of the user
#    @user_email: email of the user
#    @user_role: the role/ account type
#    """
#    # data = all_user.get(user_id, None)
#
#    # user = db.query(db_models.User).fi

@router.post("/register",
        status_code=status.HTTP_201_CREATED,
        response_model=schema.TokenResponse)
async def reg_user(payload: schema.RegisterUser, db: Session = Depends(get_db)):
    """Adds a user to the database
    check if exception occurs too, taking too long to create etc.
    """

    resp = db.query(db_models.User).filter(db_models.User.email==payload.email).first()

    if resp:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                detail="User account exist")

    temp_data = payload.dict().copy()

    temp_data["password"] = password_hash.hash_pwd(temp_data["password"])
    
    # i've done this in auth route, so a function utility should do this for
    # me instead that can now be shared across project
    db_crud.save(db, db_models.User, temp_data)
    record = db.query(db_models.User).filter(
            db_models.User.email==payload.email).first()

   # user_data = {"sub": record.user_id,
   #              "name": record.name,
   #              "email": record.email,
   #              "role": record.role}

    #resp = db_crud.get_by(db, db_models.User, email=payload.email)
    #if not resp:
    #    raise HTTPException(status_code=400, detail="account exist")
    #
    #data = {}
    #for field in resp:
    #    temp = {
    #        "user_id": field.user_id,
    #        "name": field.name,
    #        "email": field.email,
    #        "phone_num": field.phone_num,
    #        "role": field.role,
    #    }
    #    data.update(temp)

    #return {"response": "account created", "details": data}
    token = oauth2_users.create_token(record)
    return {"access_token": token, "token_type": "Bearer"}
