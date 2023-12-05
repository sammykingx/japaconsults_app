from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    status,
    UploadFile,
)
from sqlalchemy.orm import Session
from auth import oauth2_users
from models import db_engine, db_models, db_crud
from utils import google_drive as cloud
from typing import Annotated, List
from pydantic import BaseModel
from docs.routes import documents
import datetime


FOLDERS = (
    "academics",
    "billing",
    "contract",
    "general",
    "messages",
    "profile_pic",
    "visa",
)

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
        401: {"description": "Unauthorized access"},
        404: {"description": "File/Folder not found"},
        415: {"description": "Unsurpported file format"},
        500: {"description": "Internal Server Error"},
    },
)

# temp
class UploadDocuments(BaseModel):
    folder_name: str
    files: UploadFile


# temp
class UploadedFileResponse(BaseModel):
    file_name: str
    folder: str
    size: str
    file_url: str
    date_uploaded: datetime.datetime


# temp
def file_serializer(record) -> dict:
    return {
        "file_id": record.file_id,
        "name": record.name,
        "folder": record.folder,
        "file_url": record.file_url,
        "size": str(record.size) + " bytes",
        "date_uploaded": record.date_uploaded,
    }


def get_user_files(
    db: Session,
    table: db_models.Files,
    user: int,
    folderName: str | None,
) -> list[dict]:
    """serialize user files"""

    if folderName:
        if folderName not in FOLDERS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid folder specified",
            )

        records = db_crud.get_by(
            db, table, owner_id=user, folder=folderName
        )

    else:
        records = db_crud.get_by(db, table, owner_id=user)

    if not records:
        return []

    return [file_serializer(record) for record in records]


@router.post(
    "/upload",
    summary="Takes a list of files and uploads to google cloud storage",
    description="folder_name should be the name of the folder to upload to "
    "While the file should contain a list of file object."
    "Folder name: academics, billing, contract, general, visa",
    response_model=UploadedFileResponse,
    responses=documents.upload_response_codes,
)
async def upload_documents(
    folder_name: str,
    file: UploadFile,
    token: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """Uploads document to google cloud storage"""

    if folder_name not in FOLDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid destination folder",
        )
    if len(file.filename) > 45:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename greater than 45 characters",
        )

    if file.content_type not in FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsurpported file format '{file.content_type}'",
        )

    data = await file.read()
    FILE_MAX_SIZE = 3145728
    size = len(data)
    if len(data) > FILE_MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File '{file.filename}' too large",
        )

    resp = cloud.upload_file(
        "1D8rZ7oNDzwBlrOTEiqyrLDRpfb0unzhQ",
        file.filename,
        data,
        file.content_type,
    )

    date_uploaded = datetime.datetime.utcnow()

    # save to db
    db_record = {
        "file_id": resp["id"],
        "name": file.filename,
        "file_url": resp["webViewLink"].removesuffix("?usp=drivesdk"),
        "owner_id": token["sub"],
        "folder": folder_name,
        "size": len(data),
        "date_uploaded": date_uploaded,
    }

    data = db_crud.save(db, db_models.Files, db_record)

    file_resp = {
        "file_name": file.filename,
        "file_url": resp["webViewLink"].removesuffix("?usp=drivesdk"),
        "folder": folder_name,
        "size": f"{size / (1024 * 1024)}mb",
        "date_uploaded": date_uploaded,
    }

    return file_resp


# temp
class MyFiles(BaseModel):
    file_id: str
    name: str
    file_url: str
    folder: str
    size: str
    date_uploaded: datetime.datetime


@router.get(
    "/myfiles",
    summary="Get all files uploaded by the active user",
    description="returns all files owned by currently logged in user",
    response_model=list[MyFiles],
)
async def my_files(
    token: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
    folderName: str | None = None,
):
    """returns all files uploaded by the user"""

    user_files = get_user_files(
        db, db_models.Files, token["sub"], folderName
    )

    return user_files


@router.get(
    "/userfiles",
    summary="gets all the files for a specific user",
    description="should be used by admin or managers only",
    response_model=list[MyFiles],
)
async def files_for(
    user_id: int,
    token: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
    folderName: str | None = None,
):
    """returns all files uploaded by the user id"""

    if token["role"] not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthtorized access to resource",
        )

    user_files = get_user_files(db, db_models.Files, user_id, folderName)
    return user_files


@router.get(
    "/recentFiles",
    summary="Gets the recent files uploaded by the aactive user",
    description="This endpoints allows the active user to see all "
    "his/her recent files uploaded. To see recent files "
    "based on folder, pass the folder name as query param",
    response_model=list[MyFiles],
)
async def user_recent_files(
    token: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
    folderName: str | None = None,
):
    """see recent files"""

    if folderName:
        if folderName not in FOLDERS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid destination folder",
            )

        records = db_crud.record_in_lifo(
            db,
            db_models.Files,
            db_models.Files.date_uploaded,
            owner_id=token["sub"],
            folder=folderName,
        )

    else:
        records = db_crud.record_in_lifo(
            db,
            db_models.Files,
            db_models.Files.date_uploaded,
            owner_id=token["sub"],
        )

    #if not records:
    #    raise HTTPException(
    #        status_code=status.HTTP_404_NOT_FOUND,
    #        detail="No files found for user",
    #    )

    return [file_serializer(record) for record in records if record.size]


class fileByFolder(BaseModel):
    academics: list[dict]
    billing: list[dict]
    contracts: list[dict]
    general: list[dict]
    visa: list[dict]


@router.get(
    "/allFiles",
    summary="Returns all files uploaded on the system",
    description="Should only be used by previledged users in getting all "
    "files uploaded to cloud storage.",
    response_model=fileByFolder,
)
async def all_files(
    active_user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """returns all files"""

    if active_user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access to resource",
        )

    records = db_crud.get_all(db, db_models.Files)

    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="no files uploaded",
        )

    # loop
    user_folders = (
        "academics",
        "billing",
        "contracts",
        "general",
        "visa",
    )

    all_files = {}
    for folder in user_folders:
        all_files.update(
            {
                f"{folder}": [
                    file_serializer(record)
                    for record in records
                    if record.folder == folder
                ]
            }
        )

    return all_files


# temp
class DeleteFile(BaseModel):
    msg: str
    file_id: str
    file_name: str


@router.delete(
    "/removeMyFile",
    summary="Deletes files owned by logged-in user",
    description="Should be used by logged-in user in deleting files",
    response_model=DeleteFile,
)
async def remove_file(
    fileId: str,
    token: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """Deletes a file owned by the active user from cloud storage"""

    record = db_crud.get_specific_record(
        db, db_models.Files, file_id=fileId
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching file found",
        )

    if record.owner_id != token["sub"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="file not owned by active user",
        )

    db_crud.delete(db, db_models.Files, file_id=fileId)
    cloud.delete_files(fileId)
    return {
        "msg": "Deleted",
        "file_id": fileId,
        "file_name": record.name,
    }


@router.delete(
    "/removeUserFile",
    summary="removes files owned by a user",
    description="Should be used by admin or managers in deleting "
    "user files",
    response_model=DeleteFile,
)
async def remove_user_files(
    fileId: str,
    token: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """deletes file for a user, to be used by managers or admin"""

    if token["role"] not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access to resource",
        )

    record = db_crud.get_specific_record(
        db, db_models.Files, file_id=fileId
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No file found for user",
        )

    # if token["role"] != "manager":
    #    raise HTTPException(
    #        status_code=status.HTTP_401_UNAUTHORIZED,
    #        detail="Unauthorized user",
    #    )

    db_crud.delete(db, db_models.Files, file_id=fileId)
    cloud.delete_files(fileId)
    return {
        "file_id": fileId,
        "file_name": record.name,
        "msg": "Deleted",
    }
