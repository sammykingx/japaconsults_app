from sqlalchemy import Column, Integer, String, Boolean, Text
from .db_engine import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=200)
    name = Column(String(50), nullable=False)
    email = Column(String(30), index=True, unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    phone_num = Column(Integer)
    role = Column(String(20), nullable=False)

    def __rep__(self):
        return "{}, {}, {},{}, {}, {}".format(
            self.user_id,
            self.name,
            self.email,
            self.password,
            self.phone_num,
            self.role,
        )

    def __str__(self):
        return "name: {}, email: {}, phone_num: {}".format(
            self.name, self.email, self.phone_num
        )


class Drafts(Base):
    __tablename__ = "drafts"

    draft_id = Column(Integer, primary_key=True, index=True, autoincrement=200)
    user_id = Column(Integer, index=True, nullable=False)
    content = Column(Text, nullable=False)
    publish = Column(Boolean, default=False, nullable=False)
    doc_url = Column(Text)
