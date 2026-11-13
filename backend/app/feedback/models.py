"""Entities for the survey: Customer and Response (Spring: @Entity classes)."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.clock import utcnow
from app.core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    # unique + nullable: PostgreSQL allows many NULLs, but never two identical real values.
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True)
    kind: Mapped[str] = mapped_column(String(16), default="buyer")  # "buyer" or "painter"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    responses: Mapped[list["Response"]] = relationship(back_populates="customer")


class Response(Base):
    __tablename__ = "responses"
    __table_args__ = (
        CheckConstraint("product_rating BETWEEN 1 AND 5", name="ck_product_rating"),
        CheckConstraint("care_rating BETWEEN 1 AND 5", name="ck_care_rating"),
        CheckConstraint("happy_rating BETWEEN 1 AND 5", name="ck_happy_rating"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    product_rating: Mapped[int] = mapped_column(Integer)  # Q1
    care_rating: Mapped[int] = mapped_column(Integer)  # Q2
    happy_rating: Mapped[int] = mapped_column(Integer)  # Q3
    mean: Mapped[float] = mapped_column(Numeric(4, 2))  # average of the three, e.g. 2.33
    category: Mapped[str] = mapped_column(String(12), index=True)  # detractor/passive/promoter
    source: Mapped[str] = mapped_column(String(8), default="web")  # "web" or "sms"
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

    customer: Mapped[Customer] = relationship(back_populates="responses")
