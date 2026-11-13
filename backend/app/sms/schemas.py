"""DTOs for the SMS endpoints."""

from pydantic import BaseModel, Field


class SmsInviteIn(BaseModel):
    """Body of POST /api/sms/invite."""

    phone: str = Field(min_length=8, max_length=32, description="E.164, e.g. +254712345678")


class SmsInviteOut(BaseModel):
    """Reply: did the SMS provider accept the message?"""

    sent: bool
