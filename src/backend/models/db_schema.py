from sqlalchemy import Column, Integer, String, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base
from .user_roles import UserRoles

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=200)
    name = Column(String(50), nullable=False)
    email = Column(String(30), index=True, unique=True, nullable=False)
    password = Column(String, nullable=False)
    phone_num = Column(Integer)
    role = Column(Enum(UserRoles), nullable=True)

    # add a repr function for db representation


class Drafts(Base):
    __tablename__ = "drafts"

    draft_id = Column(Integer, primary_key=True, index=True, autoincrement=200)
    # am thinking of relationship here
    user_id = Column(Integer, index=True, nullable=True)
    content = Column(String, nullable=True)
    publish = Column(Boolean, default=False)
    doc_url = Column(String)
