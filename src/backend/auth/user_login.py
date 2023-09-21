from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import db_engine, db_models, schema
from utils import password_hash
from auth import oauth2_users
from typing import Annotated

router = APIRouter(prefix="/auth", tags=["Auth"])

credentials_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
)


@router.post("/", response_model=schema.TokenResponse)
async def authenticate_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(db_engine.get_db),
):
    """authenticates a user based on details sent and returns a token"""

    user = (
        db.query(db_models.User)
        .filter(db_models.User.email == form_data.username)
        .first()
    )

    if not user:
        raise credentials_exception

    if not password_hash.verify_pwd(form_data.password, user.password):
        raise credentials_exception

    token = oauth2_users.create_token(user)

    return {"access_token": token, "token_type": "Bearer"}
