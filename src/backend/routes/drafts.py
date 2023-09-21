from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import db_crud, db_engine, db_models, schema
from auth import oauth2_users


router = APIRouter(prefix="/drafts", tags=["Drafts"])


def build_drafts(record) -> dict:
    """builds a dictionary object"""

    draft = {"draft_id": record.draft_id,
             "user_id": record.user_id,
             "content": record.content,
             "doc_url": [record.doc_url],
             "date_created": record.date_created,
             "last_updated": record.last_updated
            }

    return draft


@router.get("/")
async def get_all_drafts(
        token: dict = Depends(oauth2_users.verify_token),
        db: Session = Depends(db_engine.get_db)):
    """Gets all drafts by a user from the database"""

    resp = db_crud.get_by(db, db_models.Drafts, user_id=token["sub"])
    if not resp:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="no drafts for user here")

    draft = [build_drafts(draft) for draft in resp]

    return draft


@router.post("/save", status_code=status.HTTP_201_CREATED)
async def save_drafts(
        payload: schema.CreateDrafts,
        user: dict = Depends(oauth2_users.verify_token),
        db: Session = Depends(db_engine.get_db)):
    """creates a drafts in database"""

    draft = {"user_id": user["sub"]}
    draft.update(payload.dict().copy())
    db_crud.save(db, db_models.Drafts, draft)
    return {"details": "drafts created"}


@router.patch("/update", status_code=status.HTTP_200_OK)
async def update_draft(
        payload: schema.UpdateDrafts,
        user: dict = Depends(oauth2_users.verify_token),
        db: Session = Depends(db_engine.get_db)):
    """Updates the drafts record for a particular user_id"""

    temp = payload.dict().copy()
    return {"details": "not implemented completly"}


@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_draft(
        d_id: int,
        user: dict = Depends(oauth2_users.verify_token),
        db: Session = Depends(db_engine.get_db)):
    """deletes the drafts from the record"""

    db_crud.delete(db, db_models.Drafts, draft_id=d_id)
    return {"details": "Deleted"}
