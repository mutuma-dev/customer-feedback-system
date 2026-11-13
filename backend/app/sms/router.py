"""SMS endpoints (Spring: @RestController)."""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Form

from app.alerts import notifications
from app.core.database import DbSession
from app.sms import client as sms_client
from app.sms import service
from app.sms.messages import INVITE_TEXT
from app.sms.schemas import SmsInviteIn, SmsInviteOut

router = APIRouter(prefix="/api", tags=["sms"])


@router.post("/sms/invite", response_model=SmsInviteOut)
def sms_invite(payload: SmsInviteIn) -> SmsInviteOut:
    """Send the "Rate us 1-5 ... Reply e.g. 4 5 4" invitation to a painter.

    Nothing calls this automatically. In real life Company X's sales system would call it
    after a purchase. For the demo you call it from the /docs page.
    """
    phone = service.normalise_phone(payload.phone.replace(" ", ""))
    return SmsInviteOut(sent=sms_client.send_sms(phone, INVITE_TEXT))


@router.post("/sms/incoming")
def sms_incoming(
    background: BackgroundTasks,
    db: DbSession,
    # Africa's Talking sends a FORM (not JSON) with fields named "from" and "text".
    # "from" is a reserved word in Python, so we read it under another variable name.
    sender: Annotated[str, Form(alias="from")],
    body: Annotated[str, Form(alias="text")],
) -> dict[str, str]:
    """Webhook: Africa's Talking calls this URL whenever a painter replies to our SMS."""
    result = service.process_incoming(db, sender, body)
    # Reply to the painter after we have answered Africa's Talking.
    background.add_task(sms_client.send_sms, result.phone, result.reply)
    if result.alert_id is not None:
        background.add_task(notifications.dispatch_alert, result.alert_id)
    return {"status": result.status}
