
import hashlib
import hmac
import secrets
import smtplib
from email.message import EmailMessage

from app.core.config import settings


def generate_otp() -> str:
    """Generate a cryptographically secure six-digit OTP."""
    return f"{secrets.randbelow(1000000):06d}"


def hash_otp(otp: str) -> str:
    """Hash OTP with the application's secret key."""
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        otp.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def verify_otp_hash(otp: str, stored_hash: str) -> bool:
    """Compare an entered OTP with its stored hash."""
    return hmac.compare_digest(
        hash_otp(otp),
        stored_hash,
    )


def send_otp_email(recipient: str, otp: str) -> None:
    """Send the password-reset OTP through Gmail SMTP."""
    if not all([
        settings.SMTP_USERNAME,
        settings.SMTP_APP_PASSWORD,
        settings.MAIL_FROM,
    ]):
        raise RuntimeError("Gmail SMTP settings are incomplete.")

    message = EmailMessage()
    message["Subject"] = "PhishGuard Password Reset OTP"
    message["From"] = settings.MAIL_FROM
    message["To"] = recipient

    message.set_content(
        "You requested a PhishGuard password reset.\n\n"
        f"Your verification code is: {otp}\n\n"
        "This code expires in "
        f"{settings.PASSWORD_RESET_EXPIRE_MINUTES} minutes.\n\n"
        "Do not share this code with anyone.\n"
        "If you did not request this, ignore this email."
    )

    with smtplib.SMTP(
        settings.SMTP_HOST,
        settings.SMTP_PORT,
        timeout=15,
    ) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(
            settings.SMTP_USERNAME,
            settings.SMTP_APP_PASSWORD,
        )
        smtp.send_message(message)
