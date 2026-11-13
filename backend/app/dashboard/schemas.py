"""DTOs for dashboard numbers."""

from datetime import date

from pydantic import BaseModel


class StatsOut(BaseModel):
    total: int
    detractors: int
    passives: int
    promoters: int
    avg_product: float
    avg_care: float
    avg_happy: float
    avg_mean: float


class TrendPoint(BaseModel):
    date: date
    mean: float
    count: int = 0


class TrendOut(BaseModel):
    points: list[TrendPoint]
    projection: list[TrendPoint]
