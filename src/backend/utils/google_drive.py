from fastapi import HTTPException, File, status
from pydantic import EmailStr
from googleapiclient import errors


DRIVE_EXCEPTION = HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="A network transport error occurred"
    )

def create_drive_api():
    """creates the drive api client used in communicating with google srive api"""

    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from google.auth import exceptions
    import os, pathlib

    acc_json_file = os.path.join(pathlib.Path(__file__).parent, "japaconsults-gcs.json")
    acc_cred = service_account.from_service_account_file(acc_json_file, scopes=["https://www.googleapis.com/auth/drive"])
    try:
        drive_api = build("drive", "v3", credentials=acc_cred)

    except exceptions.MutualTLSChannelError:
        raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="failed to establish connection to 3rd party service"
            )
    return drive_api


def create_folder(folder: str, parent_id: str = None):
    """creates a folder in the google drive account

    folder: The name of the folder to create
    parent_id: The parent folder ID if < FOLDER > is to be created as a sub-directory
    """

    drive = create_drive_api()
    folder_metadata = {
            "name": folder,
            "mimeType": "application/vnd.google-apps.folder"
        }
    if parent_id:
        folder_metadata.update({"parents": [parent_id]})

    try:
        resp = drive.files().create(body=folder_metadata, fields="id").execute()

    except errors.HttpError:
        raise DRIVE_EXCEPTION

    # save folder_id to db
    return resp["id"]


def folder_permission(action: str, folder_id: str, email: EmailStr):
    """creates permissions for an existing folder

    action: The desired action to take < CREATE | UPDATE >
    folder_id: The folder id
    email: The email of the user_account
    """

    drive = create_drive_api()
    permissions = {
                    "type": "user",
                    "role": "reader",
                    "emailAddress": email
        }

    if action == "create":
        try:
            resp = drive.permissions().create(fileId=folder_id, body=permissions).execute()
        except errors.HttpError:
            raise DRIVE_EXCEPTION

        return resp

    raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Action type not allowed"
        )


def file_permissions(drive, file):
    """set the permissions of the file to allow public view"""

    file_rights = {
            "type": "anyone",
            "role": "reader"
        }

    try:
        permission_resp = drive.permissions().create(fileId=file_id, body=file_rights).execute()

    except errors.HttpError:
        raise DRIVE_EXCEPTION


def upload_file(fldr_id: str, file: File, mime_type: str):
    """Uploads file to a folder existing on google drive"""
    
    from googleapiclient import http

    drive = create_drive_api()
    file_metadata = {
            "name": file.filename,
            "parents": [fldr_id]
        }

    blob = http.MediaFileUpload(file.filename, mimetype=mime_type, resumable=True)
    try:
        file = drive.files().create(body=file_metadata, media_body=blob, fields="webViewLink").execute()

    except errors.HttpError:
        raise DRIVE_EXCEPTION

    print(file)
    updated_file_rights = file_permissions(drive, blob["id"]
    print(updated_file_rights)

    return file["webViewLink"]
