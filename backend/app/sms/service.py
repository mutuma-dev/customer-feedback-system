"""Business logic for painters who answer by SMS."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.feedback import service as feedback_service
from app.sms.messages import HELP_TEXT, THANKS_TEXT
from app.sms.parser import parse_ratings


@dataclass  # a simple class that just holds data (like a Java record)
class IncomingResult:
    status: str  # "saved" or "ignored"
    phone: str  # the normalised sender, so we know where to send the reply
    reply: str  # the SMS text to send back
    alert_id: int | None = None  # set when the reply was from an unhappy customer


def normalise_phone(raw: str) -> str:
    """Always return E.164 style ("+254..."). Form encoding can turn "+" into a space."""
    return "+" + raw.strip().lstrip("+")


def process_incoming(db: Session, sender: str, body: str) -> IncomingResult:
    """Handle one SMS reply from Africa's Talking."""
    phone = normalise_phone(sender)
    ratings = parse_ratings(body)
    if ratings is None:
        # Not three numbers: do not save anything, just explain the format.
        return IncomingResult("ignored", phone, HELP_TEXT)

    # Same service the web form uses, so scoring and alerts are identical.
    _, alert = feedback_service.submit_feedback(
        db,
        name=f"Painter {phone}",  # we only know the phone number
        email=None,
        phone=phone,
        kind="painter",
        ratings=ratings,
        source="sms",
    )
    return IncomingResult("saved", phone, THANKS_TEXT, alert.id if alert else None)
