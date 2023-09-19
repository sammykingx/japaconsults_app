from fastapi import APIRouter, HTTPException
from models import schema


router = APIRouter(prefix="/drafts", tags=["Drafts"])


all_drafts = [
    {
        "user_id": 3,
        "content": "demo content",
        "publish": True,
        "doc_url": ["/path/to/doc", "url/path/to/file"],
        "date_created": "DD:MM:YY",
    },
    {
        "user_id": 2,
        "content": "the demo content",
        "publish": False,
        "doc_url": ["/doc/path"],
        "date_created": "DD:MM:YY",
    },
]


@router.get("/")
async def get_all_drafts(draft_id: int | None = None):
    """Gets all drafts from the database"""

    if not draft_id:
        return all_drafts

    if draft_id > len(all_drafts):
        raise HTTPException(status_code=404, detail="no data found, add data")

    return all_drafts[draft_id]


@router.post("/save", status_code=201)
async def save_drafts(payload: schema.CreateDrafts):
    """creates a drafts in databse"""

    all_drafts.append(payload.dict())
    return {"details": "drafts created", "draft_id": len(all_drafts)}
