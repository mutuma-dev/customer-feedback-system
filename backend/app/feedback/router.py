"""The survey endpoint (Spring: @RestController). It only handles HTTP, not business rules."""

from fastapi import APIRouter, BackgroundTasks

from app.alerts import notifications
from app.core.database import DbSession
from app.feedback import service
from app.feedback.schemas import FeedbackIn, FeedbackOut

router = APIRouter(prefix="/api", tags=["feedback"])


@router.post("/feedback", response_model=FeedbackOut, status_code=201)
def create_feedback(
    payload: FeedbackIn,  # FastAPI validates the JSON body against FeedbackIn (422 if invalid)
    background: BackgroundTasks,  # lets us run work AFTER the HTTP response is sent
    db: DbSession,  # a database session, injected by FastAPI
) -> FeedbackOut:
    """Called by the survey form. Scores the answers and alerts the care team if unhappy."""
    response, alert = service.submit_feedback(
        db,
        name=payload.name.strip(),
        email=str(payload.email).lower(),  # emails are case-insensitive: store lower case
        phone=payload.phone,
        kind=payload.kind,
        ratings=(payload.product_rating, payload.care_rating, payload.happy_rating),
        source="web",
    )
    if alert is not None:
        # Email + SMS run in the background, so the customer gets an instant answer
        # even if Gmail or the SMS service is slow.
        background.add_task(notifications.dispatch_alert, alert.id)
    return FeedbackOut(
        id=response.id,
        mean=float(response.mean),
        category=response.category,
        alert_created=alert is not None,
    )
