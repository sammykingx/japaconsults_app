from .db_engine import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    TIMESTAMP,
    JSON,
    ForeignKey
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
    password = Column(String(150), nullable=False)
    phone_num = Column(String(25), nullable=False)
    role = Column(String(20), nullable=False)
    profile_pic = Column(String(100))
    is_verified = Column(Boolean, default=False)

    def __repr_(self):
        return "User({}, {},{}, {}, {})".format(
            self.name,
            self.email,
            self.password,
            self.phone_num,
            self.role,
        )

    def __str__(self):
        return "name: {}, email: {}, phone_num: {}, role: {}".format(
            self.name, self.email, self.phone_num, self.role
        )


class Drafts(Base):
    __tablename__ = "drafts"

    draft_id = Column(
        Integer, primary_key=True, index=True, autoincrement=True
    )

    user_id = Column(Integer, index=True, nullable=False)
    title = Column(String(250), nullable=False)
    content = Column(Text, nullable=False)
    publish = Column(Boolean, default=False, nullable=False)
    doc_url = Column(JSON)
    date_created = Column(DateTime, nullable=False)
    last_updated = Column(DateTime)

    def __repr__(self):
        return "Drafts({}, {}, {}, {}, {})".format(
            self.user_id,
            self.content,
            self.publish,
            self.doc_url,
            self.date_created,
        )

    def __str__(self):
        return "user_id: {}, content: {}, publish: {}, doc_url{}".format(
            self.user_id, self.content, self.content, self.doc_url
        )


class Messages(Base):
    __tablename__ = "messages"

    msg_id = Column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    msg = Column(Text, nullable=False)
    from_id = Column(Integer, nullable=False, index=True)
    to_id = Column(Integer, nullable=False)
    docs = Column(JSON)
    sent_time = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return "Messages({}, {}, {}, {},{})".format(
            self.msg, self.from_id, self.to_id, self.doc, self.sent_time
        )

    def __str__(self):
        return "msg: {}, from: {}, to: {}, doc: {}, time_sent{}".format(
            self.msg, self.from_id, self.to_id, self.doc, self.sent_time
        )


# class Folders(Base):
#    __tablename__ = "folders"
#
#    folder_id = Cloumn(String(50), index=True, unique=True, nullable=False)
#    name = Column(String(20), index=True, unique=True, nullable=False)
#    perm_id = Cloumn(String(50), index=True, unique=True, nullable=False)
#    has_access = Cloumn(String(30), index=True, unique=True, nullable=False)


class Files(Base):
    __tablename__ = "files"

    file_id = Column(
        String(50), primary_key=True, index=True, nullable=False
    )
    name = Column(String(50), nullable=False)
    file_url = Column(String(100), nullable=False)
    owner_id = Column(Integer, nullable=False)
    folder = Column(String(50), nullable=False)

    def __repr__(self):
        return "Files({}, {}, {}. {})".format(
            self.name, self.file_url, self.owner_id, self.folder
        )

    def __str__(self):
        return "(file_name: {}, url: {}, owner_id: {}, folder: {})".format(
            self.name, self.file_url, self.owner_id, self.folder
        )


class RecievedNotes(Base):
    __tablename__ = "received_notes"

    ref_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(250))
    content = Column(Text)
    from_id = Column(Integer, nullable=False)
    from_name = Column(String(50), nullable=False)
    to_id = Column(
            Integer,
            ForeignKey("users.user_id", ondelete="SET NULL"),
            index=True
        )
    #title = Column(String(250))
    #content = Column(Text)
    sent_time = Column(DateTime)

    def __str__(self):
        return "(title: {}, content: {}, from_id: {}, to_id: {}, sent_time: {})".format(
            self.title,
            self.content,
            self.from_id,
            self.to_id,
            self.sent_time,
        )


# class Invoices(Base):
#    __tablename__ = "invoices"
#
#    inv_id = Column(Integer,
#                    primary_key=True,
#                    index=True,
#                    autoincrement=True)
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
