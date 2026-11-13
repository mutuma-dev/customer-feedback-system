"""Alert delivery: email (SMTP) and SMS to the care rep when a detractor appears.

WHEN does this run? Right after a detractor's feedback is saved (from the web form OR from an
SMS reply). It runs as a background task, i.e. after the customer already got their answer.
"""

import logging
import smtplib  # Python's built-in email-sending library
from collections.abc import Callable
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.alerts import repository
from app.core.config import get_settings
from app.core.database import SessionLocal
from app.feedback.models import Customer, Response
from app.sms import client as sms_client

log = logging.getLogger(__name__)


def build_alert_email(customer: Customer, response: Response) -> str:
    """The email text for the care rep. It contains the customer's name and email (brief rule)."""
    return (
        "A detractor needs a follow-up.\n\n"
        f"Customer: {customer.name}\nEmail: {customer.email or '-'}\n"
        f"Phone: {customer.phone or '-'}\n"
        f"Ratings - product: {response.product_rating}, care: {response.care_rating}, "
        f"happy: {response.happy_rating}\nMean: {response.mean}\nVia: {response.source}\n"
    )


def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain-text email. Returns True on success. Never raises an error."""
    settings = get_settings()
    if not settings.smtp_host:
        # Not configured: show the email in the terminal instead of sending it.
        log.info("SMTP not configured; would email %s\n%s\n%s", to, subject, body)
        return False

    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    try:
        # `with` closes the connection automatically when the block ends.
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.starttls()  # switch the connection to encrypted mode
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)
        return True
    except Exception:
        log.exception("Email to %s failed", to)
        return False


def dispatch_alert(alert_id: int, session_factory: Callable[[], Session] = SessionLocal) -> None:
    """Email and SMS the care rep, then record what was delivered on the alert.

    It opens its OWN database session, because the request's session is closed by now.
    `session_factory` is a parameter only so tests can pass a test database.
    """
    settings = get_settings()
    with session_factory() as db:
        alert = repository.find_alert(db, alert_id)
        if alert is None:
            return  # the alert vanished; nothing to do
        response = alert.response
        customer = response.customer

        # 1) Email the care rep.
        alert.email_sent = send_email(
            settings.care_rep_email,
            f"Detractor alert: {customer.name}",
            build_alert_email(customer, response),
        )
        # 2) Text the care rep (only if a phone number is configured).
        contact = customer.email or customer.phone or "no contact details"
        short = f"Detractor {response.mean}: {customer.name}, {contact}"
        if settings.care_rep_phone:
            alert.sms_sent = sms_client.send_sms(settings.care_rep_phone, short).ok
        else:
            alert.sms_sent = False  # no care phone configured
        db.commit()  # save email_sent / sms_sent
