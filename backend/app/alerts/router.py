"""HTTP endpoints for alerts (Spring: @RestController)."""

from fastapi import APIRouter

from app.alerts import service
from app.alerts.schemas import AlertOut, DraftOut
from app.core.database import DbSession

router = APIRouter(prefix="/api", tags=["alerts"])


@router.get("/alerts", response_model=list[AlertOut])
def list_alerts(db: DbSession, unread_only: bool = False):
    return service.list_alerts(db, unread_only)


@router.post("/alerts/{alert_id}/read", response_model=AlertOut)
def mark_alert_read(alert_id: int, db: DbSession):
    return service.mark_read(db, alert_id)


@router.post("/alerts/{alert_id}/draft-reply", response_model=DraftOut)
def draft_alert_reply(alert_id: int, db: DbSession) -> DraftOut:
    """AI drafts a follow-up. The care rep edits and sends it; nothing is sent from here."""
    draft, ai_used = service.create_draft(db, alert_id)
    return DraftOut(draft=draft, ai_used=ai_used)
