from email.message import EmailMessage

# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

from fastapi import HTTPException, status
from dotenv import load_dotenv
import os, smtplib


MAIL_EXCEPTION = HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    detail="Email service unavailble",
)


def send_email(message, to_addr, subject, attachment=None):
    """send email to a user mail addres using tls"""

    mail_msg = EmailMessage()
    load_dotenv()

    mail_msg["from"] = os.getenv("SMTP_MAIL")
    mail_msg["to"] = to_addr
    mail_msg["subject"] = subject
    mail_msg.add_alternative(message, subtype="html")

    try:
        with smtplib.SMTP_SSL(
            os.getenv("SMTP_HOST"), os.getenv("SMTP_PORT"), timeout=5
        ) as mail_server:
            try:
                mail_server.login(
                    os.getenv("SMTP_MAIL"), os.getenv("SMTP_PWD")
                )
                resp = mail_server.send_message(mail_msg)

            except smtplib.SMTPConnectError:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Could not establish a connection with "
                    "mail server",
                )

            except smtplib.SMTPServerDisconnected as err:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Disconnected from mail server",
                )

            except smtplib.SMTPException as err:
                raise MAIL_EXCEPTION

    except TimeoutError as err:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail=f"{err}: check internet connection",
        )

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=err
        )
