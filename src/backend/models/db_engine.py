from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os


load_dotenv()
engine = create_engine(
    os.getenv("DATABASE_URI"),
    pool_size=50,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_timeout=60,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
