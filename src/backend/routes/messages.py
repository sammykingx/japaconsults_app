from fastapi import APIRouter
from models.schema import SendMessage


router = APIRouter(prefix="/messages", tags=["Message"])

messages = {"message_id_qwe": 1,
            "from_id": 23,
            "from_details":{"sender": "John doe",
                        "email": "me@me.com",
                        "role": "user"
                        },
            "mesaage": "this is a demo message",
            "sent_time": "DD/MM/YYYY",
            "to_id": 2,
            "to_details": {"name": "james smith",
                        "email": "james@me.com",
                        "role": "manager"},
            "time stamp": "dd/mm/yyyy sec:mins:hr",
            "attachement": True,
            "doc_url": ["asdfv","verfref"]
        }
@router.get("/")
def get_messages(to_id: int | None):
    to_id_resp = {"from_id": 2,
            "msg": "the message",
            "doc": ["list of urls", "url/b/in/fs"],
            "sent_time": "DD,MM,YYYY"
            }
    return to_id_resp if to_id else messages


@router.post("/send")
async def send_msg(payload: SendMessage):
    return payload.dict()
