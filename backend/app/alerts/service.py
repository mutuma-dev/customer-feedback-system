"""Business logic for alerts (Spring: @Service)."""

from sqlalchemy.orm import Session

from app.alerts import ai, repository
from app.alerts.models import Alert
from app.core.errors import NotFoundError
from app.feedback.models import Response


def create_for_detractor(db: Session, response: Response) -> Alert:
    """Called by the feedback service. Flushes only; the caller commits."""
    return repository.save_alert(db, Alert(response_id=response.id))


def list_alerts(db: Session, unread_only: bool) -> list[Alert]:
    return repository.list_alerts(db, unread_only)


def _get(db: Session, alert_id: int) -> Alert:
    alert = repository.find_alert(db, alert_id)
    if alert is None:
        raise NotFoundError("Alert not found")
    return alert


def mark_read(db: Session, alert_id: int) -> Alert:
    alert = _get(db, alert_id)
    alert.is_read = True
    db.commit()
    return alert


def create_draft(db: Session, alert_id: int) -> tuple[str, bool]:
    """Ask the AI (or template) for a reply draft and remember it. Sends nothing."""
    alert = _get(db, alert_id)
    r = alert.response
    draft, ai_used = ai.draft_reply(
        r.customer.name, r.product_rating, r.care_rating, r.happy_rating
    )
    alert.draft_reply = draft
    db.commit()
    return draft, ai_used
