# This module contains all helper function needed in processing online payments
# The db variable used as parameter signifies the request db session

from fastapi import HTTPException, status
from models import db_models, db_crud, redis_db
from dotenv import load_dotenv
import datetime, json, requests, os


redis = redis_db.redis_factory()

def validate_invoice(db, email, invoiceId):
    """validates invoice record"""

    invoice_record = get_invoice(db, invoiceId)
    is_empty(invoice_record)
    check_assignee(email, invoice_record)
    is_expired(invoice_record)
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
        if record.status not in ("cancelled", "failed"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{record.ref_id} still active, kindly complete "
                       "transaction",
            )


def check_assignee(email, record):
    """checks if the invoice is assigned to active_user"""

    if record.to_email != email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice not assigned to active user",
        )


def is_expired(db_record):
    """checks if the invoice has expired"""

    if datetime.date.today() > db_record.due_date:
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


def cancell_transaction(db, ref):
    """ changes the payments status to cancelled

        db: the request db session
        ref: the payment reference either reference id
    """

    payment_record = get_payments_record(db, ref)
    payment_record.status = "cancelled"
    db.commit()
    db.refresh(payment_record)
    return payment_record


def failed_transaction(db, ref):
    """ changes the payments status to failed

        db: the request db session
        ref: the payment reference id
    """

    payment_record = get_payments_record(db, ref)
    payment_record.status = "failed"
    db.commit()
    db.refresh(payment_record)
    return payment_record


def update_invoice_to_paid(
    invoice_record,
    payment_record,
    payment_timestamp,
    status
):
    """updates invoices record to paid"""

    invoice_record.paid = True
    invoice_record.ref_id = payment_record.ref_id
    invoice_record.flw_txref = payment_record.flw_txRef
    invoice_record.paid_at = payment_timestamp
    invoice_record.status = status


def update_payments_to_paid(
    payment_record,
    payment_timestamp,
    payment_type,
    amount,
    status
):
    """updates the payment record to paid"""

    payment_record.paid = True
    payment_record.paid_at = payment_timestamp
    payment_record.paid_amount = amount
    payment_record.status = status
    payment_record.payment_type  = payment_type


def complete_transaction(db, refId, payment_type, amount, status):
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
            status,
        )

    update_invoice_record(
            invoice_record,
            payment_record,
            payment_timestamp,
            status
        )

    db.commit()

    db.refresh(payment_record)
    db.refresh(invoice_record)

    return invoice_record


def change_to_checking(db, refId, transaction_id):
    """changes the payment transaction status to checking"""

    payment_record = get_payments_record(db, refId)
    payment_record.flw_txRef = transaction_id
    payment_record.status = "checking"

    db.commit()
    db.refresh(payment_record)

    return payment_record


def add_transaction_id_to_redis_key(refId, transaction_id):
    """adds the transaction id gotte from payment processor to
      the redis data.

    @refId: the refId which is the redis key
    @transaction_id: the payment processor id
    """

    data = json.loads(redis.get(refId))
    data.update({"transaction_id": transaction_id})
    redis.set(refId, json.dumps(data))


def is_amount_complete(record, api_resp):
    """checks the paid amount of the customer"""

    if record.amount > api_resp["charged_amount"]:
        return True

    return False


def verv_api_call(refId, header):
    """makes the verification call using our refId to verify user payments"""

    param = {"tx_ref" : refId}
    load_dotenv()
    try:
        response = requests.get(
                        os.getenv("VERIFY_BY_REF"),
                        headers=HEADER,
                        params=param,
                        timeout=5,
                    ).json()

    except req.exceptions.ConnectionError:
        raise HTTException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="ERROR: check internet connection",
        )

    except req.exceptions.ReadTimeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="payment processor took too long to respond",
        )

    return response


def payment_serializer(ref_id, record, active_user, checkout_type):
    """serializes the payment record"""

    return {
        "ref_id": ref_id,
        #"flw_ref": flw_ref,
        #"flw_txRef": resp["txRef"],
        "inv_id": record.inv_id,
        "title": record.title,
        "amount": float(record.price),
        "payer_email": active_user["email"],
        "paid_by": active_user["name"],
        "checkout_type": checkout_type,
        "status": "pending",
    }
