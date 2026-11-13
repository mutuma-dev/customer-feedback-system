"""DTOs for alerts."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.feedback.schemas import ResponseOut


class AlertOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_read: bool
    email_sent: bool
    sms_sent: bool
    draft_reply: str | None
    created_at: datetime
    response: ResponseOut


class DraftOut(BaseModel):
    draft: str
    ai_used: bool  # False means the built-in template was used
