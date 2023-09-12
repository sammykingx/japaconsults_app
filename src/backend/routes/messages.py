from fastapi import APIRouter

router = APIRouter(prefix="/messages", tags=["Message"])

messages = {"message_id": 1,
            "sender_id": 23,
            "sender_details":{"sender": "John doe",
                        "email": "me@me.com",
                        "role": "user"
                        },
            "mesaage": "this is a demo message",
            "receiver_id": 2,
            "receeiver_details": {"name": "james smith",
                        "email": "james@me.com",
                        "role": "manager"},
            "sent_time": "dd/mm/yyyy",
            "attachement": True,
            "doc_url": ["asdfv","verfref"]
        }
@router.get("/")
def get_all_users():
    return all_user
