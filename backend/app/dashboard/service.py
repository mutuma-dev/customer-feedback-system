"""Business logic for the dashboard numbers."""

from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.clock import utcnow
from app.core.errors import NotFoundError
from app.dashboard import repository
from app.dashboard.analytics import linear_projection
from app.dashboard.schemas import StatsOut, TrendOut, TrendPoint
from app.feedback import repository as feedback_repository
from app.feedback.models import Response


def get_stats(db: Session) -> StatsOut:
    by_category = repository.count_by_category(db)
    # `v or 0.0` turns "no data" (None) into 0.0 so the dashboard shows zeros, not errors.
    product, care, happy, mean = (round(v or 0.0, 2) for v in repository.averages(db))
    return StatsOut(
        total=repository.count_all(db),
        detractors=by_category.get("detractor", 0),
        passives=by_category.get("passive", 0),
        promoters=by_category.get("promoter", 0),
        avg_product=product,
        avg_care=care,
        avg_happy=happy,
        avg_mean=mean,
    )


def get_trend(db: Session, days: int, horizon: int = 7) -> TrendOut:
    rows = repository.daily_means(db, utcnow() - timedelta(days=days))
    projection = linear_projection([(d, m) for d, m, _ in rows], horizon=horizon)
    return TrendOut(
        points=[TrendPoint(date=d, mean=m, count=n) for d, m, n in rows],
        projection=[TrendPoint(date=d, mean=m) for d, m in projection],
    )


def list_responses(db: Session, limit: int, offset: int) -> list[Response]:
    return feedback_repository.list_responses(db, limit, offset)


def get_response(db: Session, response_id: int) -> Response:
    response = feedback_repository.find_response(db, response_id)
    if response is None:
        raise NotFoundError("Response not found")
    return response
