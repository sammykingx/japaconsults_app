from fastapi import APIRouter, Depends, Form, HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_models, db_crud
from utils import google_drive as gd
from typing import Annotated, List
from pydantic import BaseModel


FOLDERS = ("academics", "billing", "general", "messages", "profile_pic")

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
        200: {"description": "Request successful"},
        413: {"description": "File 'file_name' too large"},
        401: {"description": "Unathorized, user needs to be log in"},
        404: {"description": "File/Folder not found"},
        415: {"description": "Unsurpported file format"},
        500: {"description": "Could not execute command, check back later"}
    },
)


# temp
class UploadDocuments(BaseModel):
    folder_name: str
    files: UploadFile


# temp
class UploadedFileResponse(BaseModel):
    file_name: str
    file_url: str


# temp
def file_serializer(record) -> dict:
    return {
            "file_id": record.file_id,
            "name": record.name,
            "folder": record.folder,
            "file_url": record.file_url
        }


def get_user_files(
        db: Session,
        table: db_models.Files,
        user: int) -> list[dict]:
    try:
        records = db.query(table).filter_by(owner_id=user).all()

    except Exception:
        raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="encountered some issues while processing request")

    return [file_serializer(record) for record in records]


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
    db: Annotated[Session, Depends(db_engine.get_db)]):
    """Uploads document to google cloud storage"""

    if folder_name not in FOLDERS:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid destination folder"
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
    db_record = {
            "file_id": resp["id"],
            "name": file.filename,
            "file_url": resp["webViewLink"].removesuffix("?usp=drivesdk"),
            "owner_id": token["sub"],
            "folder": folder_name
        }
    db_crud.save(db, db_models.Files, db_record)

    file_resp = {
        "file_name": file.filename,
        "file_url": resp["webViewLink"].removesuffix("?usp=drivesdk"),
    }

    return file_resp


# temp
class MyFiles(BaseModel):
    file_id: str = "12wedfsxzcvbhjuy786tyrgf"
    name: str = "file name"
    file_url: str = "uri"
    owner_id: int = 30
    folder: str = "General"


@router.get(
        "/myfiles",
        summary="Get all files uploaded by a user",
        description="returns all files owned by currently logged in user",
        response_model=list[MyFiles])
async def my_files(
        token: Annotated[dict, Depends(oauth2_users.verify_token)],
        db: Annotated[Session, Depends(db_engine.get_db)]):
    """returns all files uploaded by the user"""

   # records = (
   #         db.query(db_models.Files)
   #         .filter_by(owner_id=token["sub"])
   #         .all()
   #     )
#
#    user_files = [file_serializer(record) for record in records]
    user_files =  get_user_files(db, db_models.Files, token["sub"])
    return user_files


@router.get(
    "/userfiles",
    summary="gets all the files for a specific user",
    response_model=MyFiles,
)
async def files_for(
    uid: int,
    token: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)]):
    """returns all files uploaded by the user id"""
#
#    records = (
#            db.query(db_models.Files)
#            .filter_by(owner_id=uid)
#            .all()
#        )

    user_files =  get_user_files(db, db_models.Files, token["sub"])
    return user_files


@router.delete("/removeFile", summary="Deletes a file from the cloud storage")
async def remove_file(
        file_id: str,
        token: Annotated[dict, Depends(oauth2_users.verify_token)]
    ):
    """Deletes a file from cloud storage"""

    gd.delete_files(file_id)
    return {"detail": "file deleted successfully"}
