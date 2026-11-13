"""DTOs for the feedback feature: the exact shape of JSON going in and out.

Spring equivalent: request/response classes with Bean Validation (@Valid, @Min, @Max).
FastAPI checks incoming JSON against these classes and answers 422 if it does not match.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.feedback.scoring import Category

# A reusable rule: "a whole number between 1 and 5".
Rating = Field(ge=1, le=5)


class FeedbackIn(BaseModel):
    """Body of POST /api/feedback (what the survey form sends)."""

    name: str = Field(min_length=1, max_length=120)
    email: EmailStr  # must look like a real email address
    phone: str | None = Field(default=None, max_length=32)  # optional
    kind: Literal["buyer", "painter"] = "buyer"
    product_rating: int = Rating
    care_rating: int = Rating
    happy_rating: int = Rating


class FeedbackOut(BaseModel):
    """Reply to POST /api/feedback."""

    id: int
    mean: float
    category: Category
    alert_created: bool  # True when the customer was a detractor


class CustomerOut(BaseModel):
    """A customer as shown to the dashboard."""

    # from_attributes=True lets Pydantic read straight from a database object.
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str | None
    phone: str | None
    kind: str


class ResponseOut(BaseModel):
    """One response with its customer, used by the dashboard and the alerts."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    customer: CustomerOut
    product_rating: int
    care_rating: int
    happy_rating: int
    mean: float  # the database stores a Decimal; it is sent as a normal JSON number
    category: Category
    source: str
    created_at: datetime
