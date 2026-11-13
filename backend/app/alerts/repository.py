"""Database access for alerts."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.alerts.models import Alert
from app.feedback.models import Response


def _with_response():
    # Load alert -> response -> customer in one query.
    return select(Alert).options(joinedload(Alert.response).joinedload(Response.customer))


def save_alert(db: Session, alert: Alert) -> Alert:
    db.add(alert)
    db.flush()
    return alert


def find_alert(db: Session, alert_id: int) -> Alert | None:
    return db.scalar(_with_response().where(Alert.id == alert_id))


def list_alerts(db: Session, unread_only: bool, limit: int = 50) -> list[Alert]:
    query = _with_response().order_by(Alert.created_at.desc(), Alert.id.desc()).limit(limit)
    if unread_only:
        query = query.where(Alert.is_read.is_(False))
    return list(db.scalars(query).all())
