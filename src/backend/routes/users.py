from fastapi import APIRouter

router = APIRouter(prefix="/user", tags=["User"])

all_user = {"id": 1,
            "details": {"name": "John doe",
                        "email": "me@me.com",
                        "role": "user"
                        },
            "id": 2,
            "details": {"name": "james smith",
                        "email": "james@me.com"
                        "role": "manager"},
        }
@router.get("/")
def get_all_users():
    return all_user
