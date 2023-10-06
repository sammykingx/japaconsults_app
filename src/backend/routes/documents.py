from fastapi import APIRouter, Depends, Form, HTTPException, status, UploadFile
from auth import oauth2_users
from utils import google_drive as gd
from typing import Annotated, List
from pydantic import BaseModel
import requests as req


FOLDERS = ("academics", "billing", "general", "messages")

FILE_TYPES = (
    "image/png",
    "image/jpeg",
    "text/plain",
    "application/msword",
    "application/pdf",
    "application/vnd.ms-powerpoint",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
    responses={
        200: {"description": "File upload successful"},
        413: {"description": "File 'file_name' too large"},
        401: {"description": "Unathorized, user needs to be logged in"},
        404: {"description": "Invalid destination folder"},
        415: {"description": "Unsurpported file format"},
    },
)


class UploadDocuments(BaseModel):
    folder_name: str
    files: UploadFile


class UploadedFileResponse(BaseModel):
    file_name: str
    file_url: str


@router.post(
    "/upload",
    summary="Takes a list of files and uploads to google cloud storage",
    description="folder_name should be the name of the folder to upload to "
    "While the file should contain a list of file object."
    "folder name: academics, billing,  general, messages.",
    response_model=UploadedFileResponse,
)
async def upload_documents(
    folder_name: str,
    file: UploadFile,
    # payload: UploadDocuments,
    token: Annotated[dict, Depends(oauth2_users.verify_token)],
):
    """Uploads document to google cloud storage"""

    if folder_name not in FOLDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid destination folder"
        )
    FILE_MAX_SIZE = 3145728
    if file.content_type not in FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsurpported file format '{file.content_type}'",
        )
    data = await file.read()
    if len(data) > FILE_MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File {file.filename} too large",
        )

    resp = gd.upload_file(
        "1D8rZ7oNDzwBlrOTEiqyrLDRpfb0unzhQ", file.filename, data, file.content_type
    )

    # save to db
    file_resp = {"file_name": file.filename, "file_url": resp["webViewLink"]}

    return file_resp
