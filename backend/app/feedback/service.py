"""Business logic for submitting feedback (Spring: @Service). One method = one transaction."""

from sqlalchemy.orm import Session

from app.alerts import service as alert_service
from app.alerts.models import Alert
from app.feedback import repository
from app.feedback.models import Customer, Response
from app.feedback.scoring import classify


def _find_or_create_customer(
    db: Session, *, name: str, email: str | None, phone: str | None, kind: str
) -> Customer:
    """Re-use an existing customer (same email, else same phone) so repeat feedback is linked."""
    customer = repository.find_customer_by_email(db, email) if email else None
    if customer is None and phone:
        customer = repository.find_customer_by_phone(db, phone)
    if customer is None:
        customer = repository.save_customer(
            db, Customer(name=name, email=email, phone=phone, kind=kind)
        )
    return customer


def submit_feedback(
    db: Session,
    *,
    name: str,
    email: str | None,
    phone: str | None,
    kind: str,
    ratings: tuple[int, int, int],
    source: str,
) -> tuple[Response, Alert | None]:
    """Store a survey: find the customer, score it, raise an alert if unhappy, commit once."""
    phone = phone.replace(" ", "") if phone else None
    customer = _find_or_create_customer(db, name=name, email=email, phone=phone, kind=kind)

    mean, category = classify(*ratings)
    response = repository.save_response(
        db,
        Response(
            customer=customer,
            product_rating=ratings[0],
            care_rating=ratings[1],
            happy_rating=ratings[2],
            mean=mean,
            category=category,
            source=source,
        ),
    )
    alert = alert_service.create_for_detractor(db, response) if category == "detractor" else None
    db.commit()  # customer, response and alert are saved together or not at all
    return response, alert
