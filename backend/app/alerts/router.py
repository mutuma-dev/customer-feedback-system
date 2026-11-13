"""Alert endpoints (Spring: @RestController)."""

from fastapi import APIRouter

from app.alerts import service
from app.alerts.schemas import AlertOut, DraftOut, ReadAllOut
from app.core.database import DbSession

router = APIRouter(prefix="/api", tags=["alerts"])


@router.get("/alerts", response_model=list[AlertOut])
def list_alerts(db: DbSession, unread_only: bool = False):
    """The newest 50 alerts. `?unread_only=true` returns only the unread ones."""
    return service.list_alerts(db, unread_only)


# NOTE: "/alerts/read-all" has no variable part, so it can never be confused with
# "/alerts/{alert_id}/read".
@router.post("/alerts/read-all", response_model=ReadAllOut)
def mark_all_alerts_read(db: DbSession) -> ReadAllOut:
    """Mark every alert as read (the bell's "Mark all as read" button)."""
    return ReadAllOut(updated=service.mark_all_read(db))


@router.post("/alerts/{alert_id}/read", response_model=AlertOut)
def mark_alert_read(alert_id: int, db: DbSession):
    """Mark one alert as read."""
    return service.mark_read(db, alert_id)


@router.post("/alerts/{alert_id}/draft-reply", response_model=DraftOut)
def draft_alert_reply(alert_id: int, db: DbSession) -> DraftOut:
    """AI drafts a follow-up. The care rep edits and sends it; nothing is sent from here."""
    draft, ai_used = service.create_draft(db, alert_id)
    return DraftOut(draft=draft, ai_used=ai_used)
