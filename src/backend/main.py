# the application entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.db_engine import Base, engine
from models import db_models
from auth import user_login
from routes import documents, drafts, invoices, users, messages


Base.metadata.create_all(bind=engine)

app = FastAPI(
        title="Japaconsults User Portal",
        description="The backend application used to power the japaconsults user app",
        version="v1",
        contact={
            "name": "sammykingx",
            "url": "https://sammykingx.com.ng",
            "email": "hello@sammykingx.com.ng",
            }
    )

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# register routes
app.include_router(user_login.router)
app.include_router(documents.router)
app.include_router(drafts.router)
app.include_router(invoices.router)
app.include_router(users.router)
app.include_router(messages.router)


@app.get("/", tags=["status"])
def index():
    return {"status": "connection succesfull"}
