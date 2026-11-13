"""Endpoints the dashboard calls (Spring: @RestController)."""

from typing import Annotated

from fastapi import APIRouter, Query

from app.core.database import DbSession
from app.dashboard import service
from app.dashboard.schemas import StatsOut, TrendOut
from app.feedback.schemas import ResponseOut

router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/stats", response_model=StatsOut)
def stats(db: DbSession) -> StatsOut:
    """Headline numbers: total, the three groups and the averages."""
    return service.get_stats(db)


@router.get("/trend", response_model=TrendOut)
def trend(db: DbSession, days: Annotated[int, Query(ge=1, le=365)] = 30) -> TrendOut:
    """Daily average score for the last N days (1-365) plus a 7-day projection."""
    return service.get_trend(db, days)


@router.get("/responses", response_model=list[ResponseOut])
def list_responses(
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """Newest first. Each item includes the customer, so the dashboard can show details."""
    return service.list_responses(db, limit, offset)


@router.get("/responses/{response_id}", response_model=ResponseOut)
def get_response(response_id: int, db: DbSession):
    """One response (404 if the id does not exist)."""
    return service.get_response(db, response_id)
