from .db_engine import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    TIMESTAMP,
    ForeignKey,
    Date,
    Numeric,
)


class User(Base):
    __tablename__ = "users"

    user_id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    first_name = Column(String(25), nullable=False)
    last_name = Column(String(25), nullable=False)
    email = Column(String(50), index=True, unique=True, nullable=False)
    password = Column(String(150), nullable=False)
    phone_num = Column(String(25), nullable=False)
    role = Column(String(20), nullable=False)
    profile_pic = Column(String(100))
    is_verified = Column(Boolean, default=False)
    date_joined = Column(DateTime, nullable=False)
    last_login = Column(DateTime)

    def __repr_(self):
        return "User({}, {}, {}, {}, {}, {}, {})".format(
            self.first_name,
            self.last_name,
            self.email,
            self.password,
            self.phone_num,
            self.role,
            self.date_joined,
        )

    def __str__(self):
        return "(name: {}, email: {}, phone_num: {}, role: {})".format(
                self.first_name + self.last_name,
                self.email,
                self.phone_num,
                self.role,
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
    date_created = Column(DateTime, nullable=False)
    last_updated = Column(DateTime)

    def __repr__(self):
        return "Drafts({}, {}, {}, {}, {})".format(
            self.user_id,
            self.title,
            self.content,
            self.publish,
            self.date_created,
        )

    def __str__(self):
        return "(user ID: {}, title: {}, content: {}, publish: {})".format(
                self.user_id, self.title, self.content, self.publish
            )


class Files(Base):
    __tablename__ = "files"

    file_id = Column(
        String(50), primary_key=True, index=True, nullable=False
    )
    name = Column(String(50), nullable=False)
    file_url = Column(String(100), nullable=False)
    owner_id = Column(Integer, nullable=False)
    folder = Column(String(50), nullable=False)
    size = Column(Integer, nullable=False)
    date_uploaded = Column(DateTime, nullable=False)

    def __repr__(self):
        return "Files({}, {}, {}, {}, {}, {})".format(
            self.name,
            self.file_url,
            self.owner_id,
            self.folder,
            self.size,
            self.date_uploaded,
        )

    def __str__(self):
        return "(file_name: {}, url: {}, owner_id: {}, folder: {})".format(
                self.name, self.file_url, self.owner_id, self.folder
            )


class RecievedNotes(Base):
    __tablename__ = "received_notes"

    ref_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(250), nullable=False)
    content = Column(Text, nullable=False)
    from_id = Column(Integer, nullable=False)
    from_name = Column(String(50), nullable=False)
    to_id = Column(
        Integer,
        ForeignKey("users.user_id", ondelete="SET NULL"),
        index=True,
    )

    sent_time = Column(DateTime)

    def __repr__(self):
        return "RecievedNotes({}, {}, {}, {})".format(
            self.title, self.content, self.from_id, self.from_name
        )

    def __str__(self):
        return "(title: {}, content: {}, from_id: {}, to_id: {}, sent_time: {})".format(
            self.title,
            self.content,
            self.from_id,
            self.to_id,
            self.sent_time,
        )


class Invoices(Base):
    __tablename__ = "invoices"

    inv_id = Column(String(16), primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    desc = Column(String(100), nullable=False)
    price = Column(Numeric(precision=15, scale=2), nullable=False)
    to_email = Column(String(30), nullable=False)
    created_at = Column(DateTime, nullable=False)
    created_by = Column(String(50), nullable=False)
    due_date = Column(Date, nullable=False)
    updated_at = Column(DateTime)
    updated_by = Column(String(50))
    paid = Column(Boolean, default=False)
    status = Column(String(15))
    paid_at = Column(DateTime)
    flw_txref = Column(String(20))
    ref_id = Column(String(15))

    def __str__(self):
        return "(inv_id: {}, tile: {}, created_by: {}, to_user: {}, price: {}, due_date: {}, paid: {}, updated_at: {}, updated_by: {})".format(
                self.inv_id,
                self.title,
                self.created_by,
                self.to_email,
                self.price,
                self.due_date,
                self.paid,
                self.updated_at,
                self.updated_by,
            )


class Payments(Base):
    __tablename__ = "payments"

    ref_id = Column(
        String(15), primary_key=True, nullable=False, index=True
    )

    flw_ref = Column(String(50))
    flw_txRef = Column(String(20))
    inv_id = Column(
        String(16),
        ForeignKey("invoices.inv_id", ondelete="SET DEFAULT"),
        nullable=False,
    )

    title = Column(String(50))
    amount = Column(Numeric(precision=15, scale=2), nullable=False)
    paid = Column(Boolean, default=False)
    status = Column(String(15))
    paid_by = Column(String(30))
    payer_email = Column(String(30))
    paid_at = Column(DateTime)
    paid_amount = Column(Numeric(precision=15, scale=2))
    checkout_type = Column(String(30))
    payment_type = Column(String(15))

    def __str__(self):
        return "(refID: {}, invoiceID: {}, amount: {}, paid: {}, status: {}, client: {}, checkout_type: {}, payment_type: {}".format(
            self.ref_id,
            self.inv_id,
            self.aamount,
            self.paid,
            self.status,
            self.payer_email,
            self.checkout_type,
            self.payment_type,
        )
