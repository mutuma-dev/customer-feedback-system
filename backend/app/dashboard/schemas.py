"""DTOs for the dashboard numbers."""

from datetime import date

from pydantic import BaseModel


class StatsOut(BaseModel):
    """Headline numbers for the top of the dashboard."""

    total: int
    detractors: int
    passives: int
    promoters: int
    avg_product: float
    avg_care: float
    avg_happy: float
    avg_mean: float


class TrendPoint(BaseModel):
    """One day on the trend chart."""

    date: date
    mean: float
    count: int = 0  # number of responses that day (0 for projected days)


class TrendOut(BaseModel):
    points: list[TrendPoint]  # real data
    projection: list[TrendPoint]  # the 7-day forecast
