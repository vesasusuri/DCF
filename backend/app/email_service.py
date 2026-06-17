import logging
import smtplib
from email.message import EmailMessage

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)


def smtp_configured(settings: Settings | None = None) -> bool:
    config = settings or get_settings()
    return bool(config.smtp_host and config.smtp_from)


def send_invite_email(
    *,
    to_email: str,
    full_name: str,
    temporary_password: str,
    login_url: str,
    settings: Settings | None = None,
) -> bool:
    config = settings or get_settings()

    if not smtp_configured(config):
        logger.warning("SMTP is not configured; invite email was not sent to %s", to_email)
        return False

    subject = "Ihre Zugangsdaten für DCF Workbench"
    body = f"""Hallo {full_name},

Sie wurden zu DCF Workbench eingeladen.

Anmelden: {login_url}
E-Mail: {to_email}
Temporäres Passwort: {temporary_password}

Beim ersten Login werden Sie aufgefordert, Ihr Passwort zu ändern und Ihre E-Mail-Adresse zu bestätigen.

Mit freundlichen Grüßen
DCF Workbench · Colliers
"""

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = config.smtp_from
    message["To"] = to_email
    message.set_content(body)

    try:
        with smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=20) as server:
            if config.smtp_use_tls:
                server.starttls()
            if config.smtp_user and config.smtp_password:
                server.login(config.smtp_user, config.smtp_password)
            server.send_message(message)
        return True
    except Exception:
        logger.exception("Failed to send invite email to %s", to_email)
        return False
