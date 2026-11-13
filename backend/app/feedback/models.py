"""Entities for the survey: Customer and Response (Spring: @Entity classes).

Each class below becomes one database table.
"""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.clock import utcnow
from app.core.database import Base


class Customer(Base):
    """A person who gave feedback (a paint buyer or a painter)."""

    __tablename__ = "customers"

    # Mapped[int] says "this column holds an integer"; primary_key=True makes it auto-increment.
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    # `str | None` means the value may be empty (NULL). unique=True forbids duplicates;
    # PostgreSQL allows many NULLs in a unique column, so painters without an email are fine.
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True)
    kind: Mapped[str] = mapped_column(String(16), default="buyer")  # "buyer" or "painter"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    # Lets code write customer.responses (a list). No extra column is created.
    responses: Mapped[list["Response"]] = relationship(back_populates="customer")


class Response(Base):
    """One submitted survey (three ratings) from one customer."""

    __tablename__ = "responses"
    # CHECK constraints: the DATABASE itself refuses ratings outside 1-5,
    # even if some code had a bug.
    __table_args__ = (
        CheckConstraint("product_rating BETWEEN 1 AND 5", name="ck_product_rating"),
        CheckConstraint("care_rating BETWEEN 1 AND 5", name="ck_care_rating"),
        CheckConstraint("happy_rating BETWEEN 1 AND 5", name="ck_happy_rating"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # Foreign key to customers.id; index=True speeds up "all responses of this customer".
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), index=True)
    product_rating: Mapped[int] = mapped_column(Integer)  # Question 1
    care_rating: Mapped[int] = mapped_column(Integer)  # Question 2
    happy_rating: Mapped[int] = mapped_column(Integer)  # Question 3
    # Numeric(4, 2) = exact decimal with 2 decimals (e.g. 2.33). Never use floats for exact data.
    mean: Mapped[float] = mapped_column(Numeric(4, 2))
    # "detractor" / "passive" / "promoter". Indexed because the dashboard groups by it.
    category: Mapped[str] = mapped_column(String(12), index=True)
    source: Mapped[str] = mapped_column(String(8), default="web")  # "web" or "sms"
    # Indexed because the trend chart filters and groups by date.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, index=True
    )

    customer: Mapped[Customer] = relationship(back_populates="responses")
