from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from models import db_engine, db_models, schema
from utils import password_hash
from auth import oauth2_users
from typing import Annotated
from google_auth_oauthlib.flow import Flow
import jwt, pathlib, os


router = APIRouter(prefix="/auth", tags=["Auth"])

credentials_exception = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Invalid credentials"
)

GOOGLE_CLIENT_ID = (
    "575832262735-pimi2lkkerr3rt9h10rc2c02o0q6q9sa.apps.googleusercontent.com"
)
GOOGLE_CLIENT_SECRET = "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"
REDIRECT_URL = "http://localhost:5000/Oauth/google/callback"
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

flow = Flow.from_client_secrets_file(
    client_secrets_file=os.path.join(pathlib.Path(__file__).parent, "ls_OauthID.json"),
    scopes=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
    ],
    redirect_uri=REDIRECT_URL,
)
client_state = []


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


@router.post("/logout")
async def logout_user(token: str = Depends(oauth2_users.oauth2_scheme)):
    """revokes the user token"""

    oauth2_users.revoke_token(token)
    return {"details": "logout succesful"}


@router.post("/google/me")
async def authenticate_with_google():
    """authenticates a user with google"""

    auth_url, state = flow.authorization_url()
    client_state.append(state)
    return RedirectResponse(auth_url)


@router.get("/Oauth/google/callback", include_in_schema=False)
async def google_callback(req: Request):
    if req.query_params.get["state"] not in client_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detai="Invalid Request from client"
        )
    flow.fetch_token(authorization_response=req.url)
    credentials = flow.credentials
    user_info = jwt.decode(credentials.id_token, options={"verify_signature": False})
    print(user_info)
    return {"details": "not fully implemeted yet"}
