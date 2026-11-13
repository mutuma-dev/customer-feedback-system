"""DTOs for the feedback feature (Spring: request/response classes + Bean Validation)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.feedback.scoring import Category

Rating = Field(ge=1, le=5)  # reusable "between 1 and 5" rule


class FeedbackIn(BaseModel):
    """Body of POST /api/feedback."""

    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=32)
    kind: Literal["buyer", "painter"] = "buyer"
    product_rating: int = Rating
    care_rating: int = Rating
    happy_rating: int = Rating


class FeedbackOut(BaseModel):
    id: int
    mean: float
    category: Category
    alert_created: bool


class CustomerOut(BaseModel):
    # from_attributes lets Pydantic read straight from an entity object
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str | None
    phone: str | None
    kind: str


class ResponseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    customer: CustomerOut
    product_rating: int
    care_rating: int
    happy_rating: int
    mean: float  # database Decimal becomes a normal JSON number
    category: Category
    source: str
    created_at: datetime
