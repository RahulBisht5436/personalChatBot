import hashlib
import random
import smtplib
from email.message import EmailMessage

from streamingbackend.utility.app_config import (
    LEAD_NOTIFICATION_EMAIL,
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_TLS,
    SMTP_USER,
)


class EmailDeliveryError(Exception):
    pass


def _send_email(subject: str, to_email: str, body: str) -> None:
    if not SMTP_HOST or not SMTP_FROM:
        raise EmailDeliveryError(
            "Email is not configured. Set SMTP_HOST, SMTP_FROM, and related SMTP env vars."
        )

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = SMTP_FROM
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
            if SMTP_USE_TLS:
                server.starttls()
            if SMTP_USER and SMTP_PASSWORD:
                server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)
    except smtplib.SMTPAuthenticationError:
        raise EmailDeliveryError(
            "SMTP login failed. For Gmail, use an App Password instead of your normal password."
        ) from None
    except smtplib.SMTPException as error:
        raise EmailDeliveryError(f"Could not send email: {error}") from error
    except OSError as error:
        raise EmailDeliveryError(f"Could not reach the email server: {error}") from error


def send_otp_email(to_email: str, name: str, otp: str) -> None:
    subject = "Your Rahul AI Portfolio verification code"
    body = (
        f"Hi {name},\n\n"
        f"Your verification code is: {otp}\n\n"
        "Enter this code in the chat widget to continue the conversation.\n"
        "This code expires in 10 minutes.\n\n"
        "Rahul AI Portfolio Assistant"
    )
    _send_email(subject, to_email, body)


def send_lead_notification(lead: dict) -> None:
    subject = f"New verified portfolio chat lead: {lead['name']}"
    body = (
        "A visitor completed OTP verification and unlocked the chatbot.\n\n"
        f"Name: {lead['name']}\n"
        f"Email: {lead['email']}\n"
        f"Company: {lead['company']}\n"
        f"Designation looking for: {lead['designation']}\n"
        f"Session ID: {lead.get('session_id', 'unknown')}\n"
    )
    _send_email(subject, LEAD_NOTIFICATION_EMAIL, body)


def hash_otp(otp: str) -> str:
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()


def generate_otp() -> str:
    return f"{random.randint(0, 999999):06d}"
