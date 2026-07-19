import logging
import smtplib
from email.message import EmailMessage

from northstar.core.config import get_settings

logger = logging.getLogger("northstar.mail")


def send_auth_email(recipient: str, subject: str, body: str) -> None:
    settings = get_settings()
    if not settings.smtp_host or not settings.smtp_from_email:
        if settings.app_env.lower() == "production":
            raise RuntimeError("SMTP is not configured")
        logger.info("Development auth email for %s: %s", recipient, body)
        return

    message = EmailMessage()
    message["From"] = settings.smtp_from_email
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        if settings.smtp_starttls:
            smtp.starttls()
        if settings.smtp_username and settings.smtp_password:
            smtp.login(settings.smtp_username, settings.smtp_password)
        smtp.send_message(message)
