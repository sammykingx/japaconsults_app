from fastapi import HTTPException, File, status
from pydantic import EmailStr
from googleapiclient import errors


DRIVE_EXCEPTION = HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    detail="A network transport error occurred",
)


# tested
def create_drive_api():
    """creates the drive api client used in communicating with google srive api"""

    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from google.auth import exceptions
    import os, pathlib

    acc_json_file = os.path.join(
        pathlib.Path(__file__).parent, "japaconsults-gcs.json"
    )
    acc_cred = service_account.Credentials.from_service_account_file(
        acc_json_file, scopes=["https://www.googleapis.com/auth/drive"]
    )
    try:
        drive_api = build("drive", "v3", credentials=acc_cred)
    
    except exceptions.TransportError:
        raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="failed to establish connection to 3rd party service",
            )

    except exceptions.MutualTLSChannelError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="failed to establish connection to 3rd party service",
        )

    return drive_api


# tested
def create_folder(folder: str, parent_id: str = None):
    """creates a folder in the google drive account

    folder: The name of the folder to create
    parent_id: The parent folder ID if < FOLDER > is to be created as a sub-directory
    """

    drive = create_drive_api()
    folder_metadata = {
        "name": folder,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        folder_metadata.update({"parents": [parent_id]})

    try:
        resp = (
            drive.files()
            .create(body=folder_metadata, fields="id")
            .execute()
        )

    except errors.HttpError:
        raise DRIVE_EXCEPTION

    # save folder_id to db
    print(resp["id"])
    # perm = folder_permission("create", resp["id"], "sammykingx.tech@gmail.com")
    # print(perm)
    return resp["id"]


# not tested
def folder_permission(action: str, folder_id: str, email: EmailStr):
    """creates permissions for an existing folder

    action: The desired action to take < CREATE | UPDATE >
    folder_id: The folder id
    email: The email of the user_account
    """

    drive = create_drive_api()
    permissions = {"role": "reader", "type": "user", "emailAddress": email}

    if action == "create":
        try:
            resp = (
                drive.permissions()
                .create(fileId=folder_id, body=permissions)
                .execute()
            )
        except errors.HttpError as err:
            if err.resp.status == 400:
                print(f"cannot share folder with {email}")
                return -1
            raise DRIVE_EXCEPTION

        return resp

    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Action type not allowed",
    )


# tested
def file_permissions(drive, file_id):
    """set the permissions of the file to allow public view"""

    file_rights = {"type": "anyone", "role": "reader"}

    try:
        permission_resp = (
            drive.permissions()
            .create(fileId=file_id, body=file_rights)
            .execute()
        )

    except errors.HttpError:
        raise DRIVE_EXCEPTION

    # save the file meta to db (file_id, viewlink, file_name, user_id)
    return permission_resp


# tested
def upload_file(fldr_id: str, name: str, data, mime_type: str) -> str:
    """Uploads file to a folder existing on google drive"""

    from googleapiclient import http
    import io

    drive = create_drive_api()
    file_metadata = {"name": name, "parents": [fldr_id]}
    blob = http.MediaIoBaseUpload(
        io.BytesIO(data), mimetype=mime_type, resumable=False
    )
    try:
        file = (
            drive.files()
            .create(
                body=file_metadata,
                media_body=blob,
                fields="id, webViewLink",
            )
            .execute()
        )

    except errors.HttpError:
        raise DRIVE_EXCEPTION

    #print(file)
    updated_file_rights = file_permissions(drive, file["id"])
    #print(updated_file_rights)

    return file


# tested
def list_files(folder: bool = False):
    """list all files uploaded to cloud storage"""

    drive = create_drive_api()
    try:
        if not folder:
            # list all files and folders
            files = drive.files().list().execute()

        else:
            # list only folders
            files = (
                drive.files()
                .list(q="mimeType = 'application/vnd.google-apps.folder'")
                .execute()
            )
    except errors.HttpError:
        raise DRIVE_EXCEPTION

    #print(files)
    return files


# tested
def delete_files(file_id):
    """delete file or folder with < file_id > from cloud storage"""

    drive = create_drive_api()
    try:
        resp = drive.files().delete(fileId=file_id).execute()

    except errors.HttpError as err:
        if err.resp.status == 404:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching files to delete",
            )

        raise DRIVE_EXCEPTION
