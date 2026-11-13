"""Alert delivery: email (SMTP) and SMS to the care rep when a detractor appears."""

import logging
import smtplib
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
    """Email body for the care rep. Contains the customer's name and email"""
    return (
        "A detractor needs a follow-up.\n\n"
        f"Customer: {customer.name}\nEmail: {customer.email or '-'}\n"
        f"Phone: {customer.phone or '-'}\n"
        f"Ratings - product: {response.product_rating}, care: {response.care_rating}, "
        f"happy: {response.happy_rating}\nMean: {response.mean}\nVia: {response.source}\n"
    )


def send_email(to: str, subject: str, body: str) -> bool:
    """Send a plain-text email. Returns True on success, never raises."""
    settings = get_settings()
    if not settings.smtp_host:
        log.info("SMTP not configured; would email %s\n%s\n%s", to, subject, body)
        return False

    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
            server.starttls()
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(message)
        return True
    except Exception:
        log.exception("Email to %s failed", to)
        return False


def dispatch_alert(alert_id: int, session_factory: Callable[[], Session] = SessionLocal) -> None:
    """Background task: email and SMS the care rep, then record what was delivered.

    It opens its OWN session because the request's session is already closed by now.
    """
    settings = get_settings()
    with session_factory() as db:
        alert = repository.find_alert(db, alert_id)
        if alert is None:
            return
        response = alert.response
        customer = response.customer

        alert.email_sent = send_email(
            settings.care_rep_email,
            f"Detractor alert: {customer.name}",
            build_alert_email(customer, response),
        )
        contact = customer.email or customer.phone or "no contact details"
        short = f"Detractor {response.mean}: {customer.name}, {contact}"
        alert.sms_sent = bool(settings.care_rep_phone) and sms_client.send_sms(
            settings.care_rep_phone, short
        )
        db.commit()
