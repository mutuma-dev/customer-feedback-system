"""Database access for alerts."""

from sqlalchemy import select, update
from sqlalchemy.orm import Session, joinedload

from app.alerts.models import Alert
from app.feedback.models import Response


def _with_response():
    """Start a query that loads alert -> response -> customer in ONE SQL statement."""
    return select(Alert).options(joinedload(Alert.response).joinedload(Response.customer))


def save_alert(db: Session, alert: Alert) -> Alert:
    db.add(alert)
    db.flush()  # assigns alert.id without committing
    return alert


def find_alert(db: Session, alert_id: int) -> Alert | None:
    return db.scalar(_with_response().where(Alert.id == alert_id))


def list_alerts(db: Session, unread_only: bool, limit: int = 50) -> list[Alert]:
    """Newest first. Optionally only the unread ones."""
    query = _with_response().order_by(Alert.created_at.desc(), Alert.id.desc()).limit(limit)
    if unread_only:
        query = query.where(Alert.is_read.is_(False))
    return list(db.scalars(query).all())


def mark_all_read(db: Session) -> int:
    """Set is_read = true on every unread alert with ONE UPDATE. Returns how many changed."""
    result = db.execute(
        update(Alert)
        .where(Alert.is_read.is_(False))
        .values(is_read=True)
        .execution_options(synchronize_session=False)
    )
    return result.rowcount or 0
