"""DTOs for SMS endpoints."""

from pydantic import BaseModel, Field


class SmsInviteIn(BaseModel):
    phone: str = Field(min_length=8, max_length=32, description="E.164, e.g. +254712345678")


class SmsInviteOut(BaseModel):
    sent: bool
