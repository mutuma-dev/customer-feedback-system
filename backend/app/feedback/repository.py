"""Database access for customers and responses (Spring: JpaRepository). No business rules here."""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.feedback.models import Customer, Response


def find_customer_by_email(db: Session, email: str) -> Customer | None:
    return db.scalar(select(Customer).where(Customer.email == email))


def find_customer_by_phone(db: Session, phone: str) -> Customer | None:
    return db.scalar(select(Customer).where(Customer.phone == phone))


def save_customer(db: Session, customer: Customer) -> Customer:
    db.add(customer)
    return customer


def save_response(db: Session, response: Response) -> Response:
    db.add(response)
    db.flush()  # sends the INSERT now so response.id is available, without committing
    return response


def find_response(db: Session, response_id: int) -> Response | None:
    query = (
        select(Response).options(joinedload(Response.customer)).where(Response.id == response_id)
    )
    return db.scalar(query)


def list_responses(db: Session, limit: int, offset: int) -> list[Response]:
    query = (
        select(Response)
        .options(joinedload(Response.customer))  # load the customer in the same SQL query
        .order_by(Response.created_at.desc(), Response.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(query).all())
