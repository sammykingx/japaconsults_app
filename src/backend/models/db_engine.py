from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os


load_dotenv()
engine = create_engine(
        os.getenv("DATABASE_URI"), pool_pre_ping=True, echo=False
        )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()