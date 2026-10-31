
import smtplib
from email.message import EmailMessage

from app.core.config import settings


def send_password_reset_email(
    recipient: str,
    reset_url: str,
) -> None:
    """Send a password-reset link using configured Gmail SMTP."""

    username = settings.SMTP_USERNAME
    password = settings.SMTP_APP_PASSWORD
    sender = settings.MAIL_FROM

    if not username or not password or not sender:
        raise RuntimeError(
            "Email is not configured. Set SMTP_USERNAME, "
            "SMTP_APP_PASSWORD, and MAIL_FROM in backend/.env."
        )

    message = EmailMessage()
    message["Subject"] = "Reset your PhishGuard password"
    message["From"] = sender
    message["To"] = recipient

    message.set_content(
        "We received a request to reset your PhishGuard password.\n\n"
        f"Use the link below within "
        f"{settings.PASSWORD_RESET_EXPIRE_MINUTES} minutes:\n\n"
        f"{reset_url}\n\n"
        "If you did not request this reset, ignore this email."
    )

    with smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT,
        timeout=15,
    ) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(username, password)
        smtp.send_message(message)
