# the application entry point
from fastapi import FastAPI
from models.db_engine import engine
from models import db_schema
from routes import users, messages

app = FastAPI()

# register routes
app.include_router(users.router)
app.include_router(messages.router)

@app.get("/")
def index():
    return {"name": "sammykingx"}
