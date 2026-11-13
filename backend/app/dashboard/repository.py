"""Aggregate queries for the dashboard (counts, averages, daily means)."""

from datetime import date, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.feedback.models import Response


def count_all(db: Session) -> int:
    return db.scalar(select(func.count(Response.id))) or 0


def count_by_category(db: Session) -> dict[str, int]:
    rows = db.execute(select(Response.category, func.count()).group_by(Response.category)).all()
    return {category: count for category, count in rows}


def averages(db: Session) -> tuple[float | None, float | None, float | None, float | None]:
    row = db.execute(
        select(
            func.avg(Response.product_rating),
            func.avg(Response.care_rating),
            func.avg(Response.happy_rating),
            func.avg(Response.mean),
        )
    ).one()
    return tuple(None if v is None else float(v) for v in row)  # type: ignore[return-value]


def daily_means(db: Session, since: datetime) -> list[tuple[date, float, int]]:
    """(day, average mean, number of responses) for each day since `since`."""
    day = func.date(Response.created_at).label("day")
    rows = db.execute(
        select(day, func.avg(Response.mean), func.count())
        .where(Response.created_at >= since)
        .group_by(day)
        .order_by(day)
    ).all()
    # PostgreSQL returns a date, SQLite a string: accept both.
    return [
        (d if isinstance(d, date) else date.fromisoformat(str(d)), round(float(m), 2), int(n))
        for d, m, n in rows
    ]
