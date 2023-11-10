# the application entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from models.db_engine import Base, engine
from models import db_models
from auth import user_login
from routes import documents, drafts, invoices, users, messages, payments
from online_payments import bank_transfer, card_payments, rave_checkout
from docs import app_doc, all_tags


Base.metadata.create_all(bind=engine)

app = FastAPI(
        title="Japaconsults User Portal",
        summary=app_doc.summary,
        description=app_doc.description,
        version="v1",
        contact={
            "name": "sammykingx",
            "url": "https://sammykingx.com.ng",
            "email": "hello@sammykingx.com.ng",
            },
        license_info={
            "name": app_doc.license_name,
            "url": app_doc.license_url,
            #"identifier": "MIT",
            },
        openapi_url="/api/v1/openapi.json",
        openapi_tags=all_tags.tags_metadata,
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
app.include_router(bank_transfer.router)
app.include_router(card_payments.router)
app.include_router(rave_checkout.router)
app.include_router(payments.router)
#app.include_router(messages.router)


@app.get("/", tags=["status"])
def index():
    return {"status": "connection succesfull"}
