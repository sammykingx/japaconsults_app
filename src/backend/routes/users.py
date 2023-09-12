from fastapi import APIRouter
from models.schema import RegisterUser


router = APIRouter(prefix="/user", tags=["User"])

all_user = {1:{"name": "John doe",
                "email": "me@me.com",
                "role": "user"
                },
            2: {"name": "james smith",
                "email": "james@me.com",
                "role": "manager"
                },
            3: {"name": "sammy kingx",
                "email": "sammy@me.com",
                "role": "admin"}}


@router.get("/")
async def get_all_users():
    return all_user


@router.get("/{user_id}")
async def get_user_by_id(user_id: int):
    data = all_user.get(user_id, None)
    return data if data else {"error": "no user data"}


@router.post("/register")
async def reg_user(payload: RegisterUser):
    user_id = len(all_user) + 1
    all_user.update({user_id: payload.dict()})
    return {"action": "successful", "details": payload.dict()}
