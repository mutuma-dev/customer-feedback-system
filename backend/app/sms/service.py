"""Business logic for painters answering by SMS."""

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.feedback import service as feedback_service
from app.sms.messages import HELP_TEXT, THANKS_TEXT
from app.sms.parser import parse_ratings


@dataclass
class IncomingResult:
    status: str  # "saved" or "ignored"
    phone: str  # normalised sender, to reply to
    reply: str  # the SMS to send back
    alert_id: int | None = None


def normalise_phone(raw: str) -> str:
    """Always E.164 style: '+254...'. (Form encoding can turn '+' into a space.)"""
    return "+" + raw.strip().lstrip("+")


def process_incoming(db: Session, sender: str, body: str) -> IncomingResult:
    phone = normalise_phone(sender)
    ratings = parse_ratings(body)
    if ratings is None:
        return IncomingResult("ignored", phone, HELP_TEXT)

    _, alert = feedback_service.submit_feedback(
        db,
        name=f"Painter {phone}",
        email=None,
        phone=phone,
        kind="painter",
        ratings=ratings,
        source="sms",
    )
    return IncomingResult("saved", phone, THANKS_TEXT, alert.id if alert else None)
