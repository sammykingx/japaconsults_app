# the application entry point
from fastapi import FastAPI
from models.db_engine import Base, engine
from models import db_models
from routes import users, messages


#Base.metadata.create_all(bind=engine)


app = FastAPI()

# register routes
app.include_router(users.router)
app.include_router(messages.router)


#if __name__ == "__main__":
#    import uvicorn
#
#    uvicorn.run(app, host="0.0.0.0", port=5000)
