from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from models import db_crud, db_engine, db_models, schema
from auth import oauth2_users
from typing import Annotated
from pydantic import BaseModel
from datetime import datetime


router = APIRouter(
    prefix="/notes",
    tags=["Notes"],
    responses={
        200: {"description": "Successful Request Execution"},
        201: {"description": "Drafts Created succcessfully"},
        401: {"description": "Not Authenticated/Authorized"},
        404: {"description": "No data found"},
        500: {"description": "Internal server error"},
        501: {"description": "Not fully implemented"},
    },
)

NOT_UPDATED_EXCEPTION = HTTPException(
    status_code=status.HTTP_204_NO_CONTENT, detail="no data provided"
)


def build_drafts(record: db_models.Drafts) -> dict:
    """builds a dictionary object"""

    draft = {
        "draft_id": record.draft_id,
        "user_id": record.user_id,
        "title": record.title,
        "content": record.content,
        "date_created": record.date_created,
        "last_updated": record.last_updated,
    }

    return draft


def build_received_notes(record: db_models.RecievedNotes) -> dict:
    return {
        "title": record.title,
        "content": record.content,
        "sent_by": record.from_name,
        "sent_time": record.sent_time,
    }


@router.get(
    "/",
    summary="Gets all Notes created by the active user",
    description="Returns all notes created by the active user. "
    "If no notes found it throws a 404 error",
)
async def get_all_drafts(
    token: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """Gets all notes by a user from the database"""

    resp = db_crud.get_by(db, db_models.Drafts, user_id=token["sub"])
    if not resp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no notes found for user",
        )

    draft = [build_drafts(draft) for draft in resp]

    return draft


# temp
class NotesResponse(BaseModel):
    title: str
    content: str
    sent_by: str
    sent_time: datetime


@router.get(
    "/receivedNotes",
    summary="Returns all notes sent to the active user",
    response_model=list[NotesResponse],
)
async def receive_notes(
    user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """Get's all notes sent to current logged-in user"""

    records = db_crud.get_by(
        db, db_models.RecievedNotes, to_id=user["sub"]
    )
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No notes sent to active user",
        )

    return [build_received_notes(record) for record in records]


# temp
class SendNotes(BaseModel):
    draftId: int
    toId: int


@router.post("/sendNotes", summary="Sends a note to a user")
async def send_notes(
    payload: SendNotes,
    user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """sends notes from one user to another user"""

    if user["sub"] == payload.toId:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid request, owner_id == receiver_id",
        )
    draft = db_crud.get_specific_record(
        db, db_models.Drafts, draft_id=payload.draftId
    )

    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No notes found"
        )
    to_user = db_crud.get_specific_record(
        db, db_models.User, user_id=payload.toId
    )

    if not to_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No user with ID '{payload.toId}' found",
        )
    data = {
        "title": draft.title,
        "content": draft.content,
        "from_id": user["sub"],
        "from_name": user["name"],
        "to_id": payload.toId,
        "sent_time": datetime.utcnow(),
    }
    db_crud.save(db, db_models.RecievedNotes, data)
    # send a notification to user on the new event
    return {"msg": "Note sent successfully"}


@router.post(
    "/save",
    status_code=status.HTTP_201_CREATED,
    summary="Creates Notes for authenticated users",
)
async def save_drafts(
    payload: schema.CreateDrafts,
    user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """creates a drafts in database\n
    The Request Body parameters.\n
    @title: the tile of the draft.\n
    @content: this should be in string format with special characters properly formated.\n
    @date_created: the date the document was created, should be in datetime format.
    """

    if len(payload.title) > 248:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Number of charaters in title greater than 245",
        )

    dup_data = payload.dict().copy()
    data = {
        key: dup_data.get(key) for key in dup_data if dup_data.get(key)
    }
    draft = {"user_id": user["sub"]}
    draft.update(data)
    saved_draft = db_crud.save(db, db_models.Drafts, draft)
    return {"msg": "note created", "draft_id": saved_draft.draft_id}


@router.put("/update", status_code=status.HTTP_200_OK)
async def update_draft(
    payload: schema.UpdateDrafts,
    user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """Updates the drafts record for a particular user_id"""

    temp = payload.dict().copy()
    note = db_crud.get_specific_record(
        db, db_models.Drafts, draft_id=temp["draft_id"]
    )
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no notes found for user",
        )
    if note.user_id != user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized acccess to resource",
        )
    note.title = temp["title"]
    note.content = temp["content"]
    note.last_updated = temp["last_updated"]
    db.commit()
    db.refresh(note)

    return {"details": "note updated"}


@router.delete(
    "/delete",
    status_code=status.HTTP_200_OK,
    summary="Deletes the specified notes from the database",
)
async def delete_draft(
    d_id: int,
    user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """deletes the drafts from the record"""

    draft = db_crud.get_specific_record(
        db, db_models.Drafts, draft_id=d_id
    )
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no notes found to delete found",
        )
    if draft.user_id != user["sub"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="note not owned by active user",
        )
    db_crud.delete(db, db_models.Drafts, draft_id=d_id)
    return {"msg": "Deleted"}
