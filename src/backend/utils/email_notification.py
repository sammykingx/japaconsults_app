from email.message import EmailMessage
from fastapi import HTTPException, status
from dotenv import load_dotenv
import os, smtplib


MAIL_EXCEPTION = HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Email service unavailble"
)


def send_email(message, to_addr, subject, attachment=None):
    """send email to a user mail addres using tls"""

    mail_msg = EmailMessage()
    load_dotenv()

    mail_msg["from"] = os.getenv("SMTP_MAIL")
    mail_msg["to"] = to_addr
    mail_msg["subject"] = subject
    mail_msg.set_content(message)

    with smtplib.SMTP_SSL(
        os.getenv("SMTP_HOST"), os.getenv("SMTP_PORT"), timeout=15
    ) as mail_server:
        try:
            # print("login into mail_Server")
            mail_server.login(os.getenv("SMTP_MAIL"), os.getenv("SMTP_PWD"))
            # print("Login successfull, sending mail to user")
            resp = mail_server.send_message(mail_msg)
            # print("message sent to user")

        except smtplib.SMTPConnectError:
            print("could not connect to server")

        except smtplib.SMTPException as err:
            print(f"SMTPException: {err}")
            raise MAIL_EXCEPTION
