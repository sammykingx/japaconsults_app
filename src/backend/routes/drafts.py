from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import db_crud, db_engine, db_models, schema
from auth import oauth2_users


router = APIRouter(prefix="/drafts", tags=["Drafts"])

NOT_UPDATED_EXCEPTION = HTTPException(
        status_code=status.HTTP_204_NO_CONTENT,
        detail="no data provided")

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
                detail="no drafts found for user")

    draft = [build_drafts(draft) for draft in resp]

    return draft


@router.post("/save", status_code=status.HTTP_201_CREATED)
async def save_drafts(
        payload: schema.CreateDrafts,
        user: dict = Depends(oauth2_users.verify_token),
        db: Session = Depends(db_engine.get_db)):
    """creates a drafts in database\n
    The Request Body parameters\n
    @content: this should be in string format with special characters properly formated.\n
    @doc_url: a list of doc_url e.g ["path/to/file1, "oat_2_.jpg"] if no doc passed it should not be added to the payload.\n
    @date_created: the date the document was created, should be in datetime format.
    """

    dup_data = payload.dict().copy()
    data = {key: dup_data.get(key) for key in dup_data if dup_data.get(key)}
    draft = {"user_id": user["sub"]}
    draft.update(data)
    print(draft)
    db_crud.save(db, db_models.Drafts, draft)
    return {"details": "drafts created"}


@router.put("/update", status_code=status.HTTP_200_OK)
async def update_draft(
        payload: schema.UpdateDrafts,
        user: dict = Depends(oauth2_users.verify_token),
        db: Session = Depends(db_engine.get_db)):
    """Updates the drafts record for a particular user_id"""

    temp = payload.dict().copy()
    try:
        draft = db.query(db_models.Drafts).filter_by(draft_id=temp["draft_id"]).first()

    except Exception as err:
        # send mail
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="oopsy !! could not execute this, try in 2hrs time")

    if not draft:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="no drafts found for user")

    draft.content = temp["content"]
    draft.doc_url = temp["doc_url"]
    draft.last_updated = temp["last_updated"]
    db.commit()
    db.refresh(draft)

    return {"details": "drafts updated"}


@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_draft(
        d_id: int,
        user: dict = Depends(oauth2_users.verify_token),
        db: Session = Depends(db_engine.get_db)):
    """deletes the drafts from the record"""

    db_crud.delete(db, db_models.Drafts, draft_id=d_id)
    return {"details": "Deleted"}
