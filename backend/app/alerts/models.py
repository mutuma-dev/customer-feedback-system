"""Entity for detractor alerts (one row per unhappy response)."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.clock import utcnow
from app.core.database import Base
from app.feedback.models import Response


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(primary_key=True)
    # unique=True: a response can raise at most ONE alert.
    response_id: Mapped[int] = mapped_column(ForeignKey("responses.id"), unique=True)
    # Has a care rep marked it as read? Drives the unread badge on the dashboard bell.
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    # Did the care-team email / SMS really go out? (False if Gmail or the SMS service failed)
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    sms_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    # The last reply draft that was generated for this alert.
    draft_reply: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Lets code write alert.response.customer.name
    response: Mapped[Response] = relationship()
