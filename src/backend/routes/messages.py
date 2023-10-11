from fastapi import APIRouter, Depends
from models.schema import SendMessage
from auth import oauth2_users

router = APIRouter(prefix="/messages", tags=["Message"])

messages = [
    {
        "message_id_qwe": 1,
        "from_id": 23,
        "from_details": {
            "sender": "John doe",
            "email": "me@me.com",
            "role": "user",
        },
        "mesaage": "this is a demo message",
        "sent_time": "DD/MM/YYYY",
        "to_id": 2,
        "to_details": {
            "name": "james smith",
            "email": "james@me.com",
            "role": "manager",
        },
        "time_stamp": "dd/mm/yyyy sec:mins:hr",
        "attachement": True,
        "doc_url": ["asdfv", "verfref"],
    }
]


@router.get("/")
def get_messages(user: dict = Depends(oauth2_users.verify_token)):
    """gets messages from the db

    when you query the root you get all the messages, however when to provide an id it gets all messages sent to that id provided
    """
    to_id_resp = {
        "from_id": 2,
        "msg": "the message",
        "doc": ["list of urls", "url/b/in/fs"],
        "sent_time": "DD,MM,YYYY",
    }
    return to_id_resp


@router.post("/send")
async def send_msg(
    payload: SendMessage = Depends(oauth2_users.verify_token),
):
    return payload.dict()
