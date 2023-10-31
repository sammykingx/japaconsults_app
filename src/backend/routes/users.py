from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
    UploadFile,
)
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from models import db_engine, db_crud, db_models, schema
from auth import oauth2_users
from utils import email_notification, password_hash, verify_number
from utils import google_drive as cloud
from typing import Annotated, Dict, List
from pydantic import BaseModel, EmailStr
import datetime, jwt


router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={
        200: {"description": "Successful request"},
        201: {"description": "Account created"},
        400: {"description": "Missing required data to process request"},
        401: {"description": "Unauthorized access to resource"},
        403: {"description": "Cannot access resource"},
        404: {"description": "Resource Not Found"},
        405: {"description": "Incorrect HTTP Method used by client"},
        413: {"description": "File too large"},
        415: {"description": "Unsupported file type"},
        500: {"description": "Internal server error"},
    },
)


USER_ROLES = ("admin", "user", "manager", "staff")

templates = Jinja2Templates(directory="templates")


def serialize_user(user: db_models.User) -> dict:
    """builds the user_json object"""

    data = {
        "user_id": user.user_id,
        "name": f"{user.first_name} {user.last_name}",
        "email": user.email,
        "phone_num": user.phone_num,
        "role": user.role,
        "is_verified": user.is_verified,
        "profile_pic": user.profile_pic,
        "date_joined": user.date_joined,
        "last_login": user.last_login,
    }
    return data


def check_user_payload(payload):
    """verifies the user payload"""

    if len(payload.first_name) > 25 or len(payload.last_name) > 25:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="name field should be less than 25 characters",
        )

    if len(payload.email) > 29:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="email length too long",
        )
    if payload.role not in USER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid user role",
        )
    if not verify_number.verify_phone_num(payload.phone_num):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Phone number format",
        )


# temp
class AllUsersResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    phone_num: str
    role: str
    is_verified: bool
    profile_pic: str | None
    date_joined: datetime.datetime | None
    last_login: datetime.datetime | None


@router.get(
    "/",
    summary="Gets all verified user accounts on the system",
    description="This endpoint should be used by users with role 'admin' only.",
    response_model=list[AllUsersResponse],
)
async def get_users(
    user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """gets all user role account in the user table"""

    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access to resource",
        )

    users = db_crud.get_all(db, db_models.User)
    if not users:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users on the system",
        )

    all_users = [
        serialize_user(user) for user in users if user.is_verified
    ]
    return all_users


@router.get(
    "/allUsers",
    summary="Returns all account with role 'user'",
    description="Returns all 'user' role accounts. Should only be used by "
    "previledged users.",
    response_model=list[AllUsersResponse],
)
async def all_users(
    user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """gets all accounts of role 'user'"""

    if user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access to resource",
        )

    records = db_crud.get_by(db, db_models.User, role="user")
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user with role 'user' found",
        )
    return [serialize_user(record) for record in records]


@router.get(
    "/staffs",
    summary="Returns all accounts of type 'staff'",
    description="This endpoint allows you to get all account "
    "with role 'staff'. Should not be used by users "
    "with role type 'user'",
    response_model=list[AllUsersResponse],
)
async def all_staffs(
    user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """get all staffs"""

    if user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access to resource",
        )

    records = db_crud.get_by(db, db_models.User, role="staff")
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No staff found on the system",
        )
    return [serialize_user(record) for record in records]


@router.get(
    "/managers",
    summary="Returns all user accounts of role type 'manager'",
    description="Should be used by admin or managers only",
    response_model=list[AllUsersResponse],
)
async def all_managers(
    user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """returns all managers"""

    if user["role"] in ("staff", "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access to resource",
        )

    records = db_crud.get_by(db, db_models.User, role="manager")
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No managers found",
        )
    return [serialize_user(record) for record in records]


@router.get(
    "/allAdmin",
    summary="Returns all administrators",
    description="This endpoint should only be used by admin",
    response_model=list[AllUsersResponse],
)
async def all_admins(
    user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """get all admins"""

    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access to resource",
        )

    records = db_crud.get_by(db, db_models.User, role="admin")
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No admin found"
        )
    return [serialize_user(record) for record in records]


# temp
class ProfileResponse(BaseModel):
    name: str
    email: EmailStr
    phone_num: str
    role: str
    profile_pic: str | None
    is_verified: bool
    date_joined: datetime.datetime


@router.get(
    "/profile",
    summary="Gets the current user profile details",
    response_model=AllUsersResponse,
)
async def user_profile(
    token: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
) -> dict:
    """return the users details"""

    record = db_crud.get_specific_record(
        db, db_models.User, user_id=token["sub"]
    )
    profile = serialize_user(record)
    return profile


@router.get(
    "/{userId}",
    summary="Returns the details of a specific user",
    description="This endpoint returns the details of a specific user"
    "Should not be used by users with role 'user'.",
    response_model=AllUsersResponse,
)
async def user_details_by_id(
    userId: int,
    user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """gets a user record by the id specified"""

    if user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access to resource",
        )
    record = db_crud.get_specific_record(
        db, db_models.User, user_id=userId
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching user found",
        )

    user = serialize_user(record)
    return user


# temp
class UserRegistrationToken(BaseModel):
    msg: str
    status: str


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="creates a user account",
    description="Creates an unverified user account",
    response_model=UserRegistrationToken,
)
async def register_user(
    payload: schema.RegisterUser,
    db: Annotated[Session, Depends(db_engine.get_db)],
    req: Request,
):
    """Adds a user to the database"""

    check_user_payload(payload)
    resp = db_crud.get_specific_record(
        db, db_models.User, email=payload.email
    )
    if resp:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User account exists",
        )

    temp_data = payload.dict().copy()
    temp_data["password"] = password_hash.hash_pwd(temp_data["password"])
    temp_data.update(date_joined=datetime.datetime.utcnow())
    db_crud.save(db, db_models.User, temp_data)
    # email_token = oauth2_users.email_verification_token(payload.email)
    # message = templates.TemplateResponse(
    #        "email_verification.html",
    #        {
    #            "user": temp_data["name"],
    #            "email_token": email_token,
    #            "request": req
    #        },
    #    ).body.decode()
    # email_notification.send_email(
    #    message, temp_data["email"], "WELCOME EMAIL")

    return {
        "msg": "user account created succefully",
        "status": "Unverified",
    }


@router.patch(
    "/changeRole",
    summary="Updates the user profile",
    description="Updates the role of a user, this should only be used"
    "by admin or managers.",
)
async def change_user_role(
    payload: schema.ChangeUserRole,
    user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """Updates the existing record of the user to the information
    provided on the payload
    """

    # checks active user role
    if user["role"] not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized access to resource",
        )

    # checks the request payload role
    if payload.role not in USER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user role selected",
        )
    record = db_crud.get_specific_record(
        db, db_models.User, email=payload.user_email
    )
    if not record:
        raise HTTPexception(
            status_code=status.HTTP_404_NOT_FOUND, detail="No user found"
        )
    if record.role == "manager":
        if payload.role in ("user", "staff") and user["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"only admin can demote '{record.role}'",
            )

    record.role = payload.role
    db.commit()
    db.refresh(record)
    user_data = {
        "user_id": record.user_id,
        "name": record.name,
        "email": record.email,
        "role": payload.role,
    }
    return {"msg": "role updated", "data": user_data}


@router.post(
    "/profilePic",
    summary="Uploads a user profile picture",
    description="User profile picture shoud not be more than 700kb",
)
async def user_profile_pic(
    file: UploadFile,
    user: Annotated[dict, Depends(oauth2_users.verify_token)],
    db: Annotated[Session, Depends(db_engine.get_db)],
):
    """uploads profile picture"""

    file_types = ("image/png", "image/jpeg")
    file_size = 700000

    if file.content_type not in file_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File type 'file.content_type' not supported",
        )
    data = await file.read()
    if len(data) > file_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size too large",
        )
    resp = cloud.upload_file(
        "1D8rZ7oNDzwBlrOTEiqyrLDRpfb0unzhQ",
        file.filename,
        data,
        file.content_type,
    )
    record = db_crud.get_specific_record(
        db, db_models.User, user_id=user["sub"]
    )
    record.profile_pic = resp["webViewLink"].removesuffix("?usp=drivesdk")
    try:
        db.commit()
        db.refresh(record)
    except Exception as err:
        print(err)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="upload successful, however an issue occurred whilst"
            "saving your image.",
        )

    return {"msg": "upload succesfull"}
