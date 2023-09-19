# the application entry point
from fastapi import FastAPI
from models.db_engine import Base, engine
from models import db_models
from auth import user_login
from routes import drafts, users, messages


Base.metadata.create_all(bind=engine)


app = FastAPI()

# register routes
app.include_router(user_login.router)
app.include_router(drafts.router)
app.include_router(users.router)
app.include_router(messages.router)


@app.get("/", tags=["Index"])
def index():
    return {"status": "connection succesfull"}
