from fastapi import APIRouter, Depends, Form, HTTPException, status, UploadFile
from auth import oauth2_users
from typing import Annotated, List
from pydantic import BaseModel


FOLDERS = ("academics", "billing",  "general", "messages")

router = APIRouter(
        prefix="/documents",
        tags=["Documents"],
        responses={
            200: {"description": "File upload successful"},
            413: {"description": "File too large"},
            401: {"description": "Unathorized, user needs to be logged in"},
            404: {"description": "Invalid destination folder"}
            }
    )

class UploadDocuments(BaseModel):
    folder_name: str
    files: List[UploadFile]


@router.post("/upload",
        summary="Takes a list of files and uploads to google cloud storage",
        description="folder_name should be the name of the folder to upload to " \
                "While the files should contain a list of file object")
async def upload_documents(
        folder_name: str,
        files: List[UploadFile],
        #payload: UploadDocuments,
        token: Annotated[dict, Depends(oauth2_users.verify_token)]):
    """Uploads documents to google cloud storage"""


    if folder_name not in FOLDERS:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid destination folder"
            )
    FILE_MAX_SIZE = 3145728
    for file in files:
        data = await file.read()
        if len(data) > FILE_MAX_SIZE:
            raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    details=f"{file.filename} too large")

    return {"details": "files uploaded"}
