# the application entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.db_engine import Base, engine
from models import db_models
from auth import user_login
from routes import drafts, users, messages


Base.metadata.create_all(bind=engine)


app = FastAPI()

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# register routes
app.include_router(user_login.router)
app.include_router(drafts.router)
app.include_router(users.router)
app.include_router(messages.router)


@app.get("/", tags=["status"])
def index():
    return {"status": "connection succesfull"}
