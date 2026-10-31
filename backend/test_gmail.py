
import smtplib
from email.message import EmailMessage

from app.core.config import settings

message = EmailMessage()
message["Subject"] = "PhishGuard Gmail Test"
message["From"] = settings.MAIL_FROM
message["To"] = settings.SMTP_USERNAME
message.set_content(
    "Success! Gmail SMTP is working for PhishGuard OTP delivery."
)

with smtplib.SMTP(
    settings.SMTP_HOST,
    settings.SMTP_PORT,
    timeout=20,
) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(
        settings.SMTP_USERNAME,
        settings.SMTP_APP_PASSWORD,
    )
    smtp.send_message(message)

print("SUCCESS: Test email sent. Check your Gmail inbox and Spam folder.")
