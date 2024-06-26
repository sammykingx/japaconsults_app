# This module contains all helper function needed in processing online payments
# The db variable used as parameter signifies the request db session

from fastapi import HTTPException, status
from models import db_engine, db_models, db_crud, redis_db
from dotenv import load_dotenv
import datetime, json, requests, os


redis = redis_db.redis_factory()


def validate_invoice(db, email, invoiceId):
    """validates invoice record"""

    invoice_record = get_invoice(db, invoiceId)
    is_empty(invoice_record)
    is_paid(invoice_record)
    check_assignee(email, invoice_record)
    is_expired(db, invoice_record)
    has_active_payment(db, invoiceId)
    return invoice_record


def has_active_payment(db, invoiceId):
    """checks if the user has an active payment process"""

    payment_records = db_crud.get_by(
        db, db_models.Payments, inv_id=invoiceId
    )

    if not payment_records:
        return False

    for record in payment_records:
        if record.status == "pending":
            update_payment_status(db, record, "cancelled")

        elif record.status == "checking":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="we're still verifying transaction with refId "
                f"{record.ref_id}",
            )


def is_paid(record):
    """checks if the invoice is already paid"""

    if record.paid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice is already paid",
        )


def check_assignee(email, record):
    """checks if the invoice is assigned to active_user"""

    if record.to_email != email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice not assigned to active user",
        )


def is_expired(db, db_record):
    """checks if the invoice has expired"""

    if datetime.date.today() > db_record.due_date:
        update_invoice_status(db, db_record, "expired")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice has expired, can't process payment",
        )


def is_empty(db_record):
    """checks the db record if its empty"""

    if not db_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No matching invoice found, check invoice ID",
        )


def get_invoice(db, invoiceId):
    """returns the invoice record"""

    record = db_crud.get_specific_record(
        db, db_models.Invoices, inv_id=invoiceId
    )

    return record


def get_payments_record(db, refId):
    """gets the payment record

    db: the request db session
    refId: the payment reference id
    """

    record = db_crud.get_specific_record(
        db, db_models.Payments, ref_id=refId
    )

    return record


def update_invoice_record(
    invoice_record, payment_record, payment_timestamp, tx_status
):
    """updates invoices record"""

    invoice_record.paid = True
    invoice_record.ref_id = payment_record.ref_id
    invoice_record.flw_txref = payment_record.flw_txRef
    invoice_record.paid_at = payment_timestamp
    invoice_record.status = tx_status


def update_payments_record(
    payment_record,
    payment_timestamp,
    payment_type,
    amount,
    tx_status,
    flw_ref=None,
):
    """updates the payment record to paid"""

    if flw_ref:
        payment_record.flw_ref = flw_ref

    payment_record.paid = True
    payment_record.paid_at = payment_timestamp
    payment_record.paid_amount = amount
    payment_record.status = tx_status
    payment_record.payment_type = payment_type


def complete_transaction(
    db, refId, payment_type, amount, tx_status, flw_ref
):
    """updates the payments and invoice table upon successfull payments"""

    payment_timestamp = datetime.datetime.utcnow()

    # get records
    payment_record = get_payments_record(db, refId)
    invoice_record = get_invoice(db, payment_record.inv_id)

    # update records
    update_payments_record(
        payment_record,
        payment_timestamp,
        payment_type,
        amount,
        tx_status,
        flw_ref,
    )

    update_invoice_record(
        invoice_record, payment_record, payment_timestamp, tx_status
    )

    db.commit()

    db.refresh(payment_record)
    db.refresh(invoice_record)

    return invoice_record


def change_to_checking(db, payment_record, transaction_id, tx_status):
    """changes the payment transaction status to checking"""

    #    payment_record = get_payments_record(db, refId)
    payment_record.flw_txRef = transaction_id
    payment_record.status = tx_status

    db.commit()
    db.refresh(payment_record)

    return payment_record


def update_payment_status(db, payment_record, tx_status):
    """updates the payment status"""

    #    payment_record = get_payments_record(db, refId)
    payment_record.status = tx_status

    db.commit()
    db.refresh(payment_record)


def update_invoice_status(db, invoice_record, tx_status):
    """updates the invoice status"""

    invoice_record.status = tx_status

    db.commit()
    db.refresh(invoice_record)


def add_transaction_id_to_redis_key(refId, transaction_id):
    """adds the transaction id gotte from payment processor to
      the redis data.

    @refId: the refId which is the redis key
    @transaction_id: the payment processor id
    """

    data = json.loads(redis.get(refId))
    data.update({"transaction_id": transaction_id})
    redis.set(refId, json.dumps(data))


def is_amount_complete(record, data):
    """checks the paid amount of the customer"""

    if data["charged_amount"] >= record.amount:
        return True

    return False


def verv_api_call(refId, header):
    """makes the verification call using our refId to verify user payments"""

    param = {"tx_ref": refId}
    load_dotenv()
    try:
        response = requests.get(
            os.getenv("VERIFY_BY_REF"),
            headers=header,
            params=param,
            timeout=5,
        ).json()

    except requests.exceptions.ConnectionError:
        raise HTTException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="ERROR: check internet connection",
        )

    except requests.exceptions.ReadTimeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="payment processor took too long to respond",
        )

    print("inside verv api call\n", response, "\n")

    return response


def confirm_user_payments(refId, header):
    """confirm users payments with rave"""

    db_session = next(db_engine.get_db())

    payment_record = get_payments_record(db_session, refId)

    resp = verv_api_call(refId, header)
    if resp["status"] != "success":
        update_payment_status(db_session, payment_record, resp["status"])

        return {
            "status": resp["status"],
            "msg": "check back later",
        }

    if is_amount_complete(payment_record, resp["data"]):
        tx_status = "paid"

    else:
        tx_status = "incomplete"

    complete_transaction(
        db_session,
        refId,
        resp["data"]["payment_type"],
        resp["data"]["charged_amount"],
        tx_status,
        resp["data"]["flw_ref"],
    )

    redis.delete(refId)

    return {
        "status": resp["status"],
        "msg": "payment verified",
    }


def payment_serializer(
    ref_id, record, active_user, checkout_type, flw_txref=None
):
    """serializes the payment record"""

    data = {
        "ref_id": ref_id,
        "inv_id": record.inv_id,
        "title": record.title,
        "amount": float(record.price),
        "payer_email": active_user["email"],
        "paid_by": active_user["name"],
        "checkout_type": checkout_type,
        "status": "pending",
    }

    if flw_txref:
        data.update({"flw_txRef": flw_txref})

    return data
