from .db_engine import Base
from sqlalchemy import (
        Column,
        Integer,
        String,
        Boolean,
        Text,
        DateTime,
        TIMESTAMP,
        JSON
    )

class User(Base):
    __tablename__ = "users"

    user_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    name = Column(String(50), nullable=False)
    email = Column(String(30), index=True, unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    phone_num = Column(String(25))
    role = Column(String(20), nullable=False)
    #profile_pic = Column(String(30))

    def __repr_(self):
        return "User({}, {}, {},{}, {}, {})".format(
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

    draft_id = Column(
        Integer, primary_key=True, index=True, autoincrement=True
    )

    user_id = Column(Integer, index=True, nullable=False)
    content = Column(Text, nullable=False)
    publish = Column(Boolean, default=False, nullable=False)
    doc_url = Column(JSON)
    date_created = Column(DateTime, nullable=False)
    #last_updated = Column(DateTime)

    def __repr__(self):
        return "Drafts({}, {}, {}, {}, {}, {})".format(
            self.draft_id,
            self.user_id,
            self.content,
            self.publish,
            self.doc_url,
            self.date_created
        )

    def __str__(self):
        return "user_id: {}, content: {}, publish: {}, doc_url{}".format(
            self.user_id, self.content, self.content, self.doc_url
        )


class Messages(Base):
    __tablename__ = "messages"

    msg_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    msg = Column(Text, nullable=False)
    from_id = Column(Integer, nullable=False, index=True)
    to_id = Column(Integer, nullable=False)
    docs = Column(JSON)
    sent_time = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return "Messages({},{}, {}, {}, {},{})".format(
            self.msg_id, self.msg, self.from_id, self.to_id, self.doc, self.sent_time
        )

    def __str__(self):
        return "msg: {}, from: {}, to: {}, doc: {}, time_sent{}".format(
            self.msg, self.from_id, self.to_id, self.doc, self.sent_time
        )


#class Invoices(Base):
#    __tablename__ = "invoices"
#
#    inv_id = Column(iInteger, primary_key=True, index=True, autoincrement=True)
#    from_uid = Column(Integer)
#    to_uid = Column(Integer)
#    paid = Column(Boolean, default=False, nullable=True)
#
#    def __repr__(self):
#        return "Invoices({}, {}, {}, {})".format(
#            self.inv_id, self.from_uid, self.to_uid, self.paid
#        )
#
#    def __str__(self):
#        return "(inv_id: {}, from_user: {}, to_user: {}, paid: {})".format(
#            self.inv_id, self.from_uid, self.to_uid, self.paid
#        )
