"""Business logic for submitting feedback (Spring: @Service).

One public function = one transaction: everything is saved together or not at all.
"""

from sqlalchemy.orm import Session

from app.alerts import service as alert_service
from app.alerts.models import Alert
from app.feedback import repository
from app.feedback.models import Customer, Response
from app.feedback.scoring import classify


def _find_or_create_customer(
    db: Session, *, name: str, email: str | None, phone: str | None, kind: str
) -> Customer:
    """Re-use an existing customer (same email, else same phone) so repeat feedback is linked.

    A leading underscore in the name means "private helper, used only in this file".
    """
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
    *,  # everything after the star must be passed by name (clearer at the call site)
    name: str,
    email: str | None,
    phone: str | None,
    kind: str,
    ratings: tuple[int, int, int],
    source: str,
) -> tuple[Response, Alert | None]:
    """Store a survey: find the customer, score it, raise an alert if unhappy, commit once.

    Used by BOTH the web form (source="web") and SMS replies (source="sms"),
    so scoring and alerts behave identically for both.
    """
    phone = phone.replace(" ", "") if phone else None  # "+254 712 ..." -> "+254712..."
    customer = _find_or_create_customer(db, name=name, email=email, phone=phone, kind=kind)

    mean, category = classify(*ratings)  # the * unpacks the tuple into three arguments
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
    # Only unhappy customers raise an alert (the brief's rule).
    alert = alert_service.create_for_detractor(db, response) if category == "detractor" else None
    db.commit()  # customer + response + alert are saved together, or not at all
    return response, alert
