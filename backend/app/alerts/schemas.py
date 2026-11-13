"""DTOs for alerts."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.feedback.schemas import ResponseOut


class AlertOut(BaseModel):
    """An alert with the full response and customer, so the card can show everything."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_read: bool
    email_sent: bool
    sms_sent: bool
    draft_reply: str | None
    created_at: datetime
    response: ResponseOut


class DraftOut(BaseModel):
    """Reply of the "draft a reply" endpoint."""

    draft: str
    ai_used: bool  # False means the built-in template was used instead of the AI


class ReadAllOut(BaseModel):
    """Reply of the "mark all as read" endpoint: how many alerts were changed."""

    updated: int
