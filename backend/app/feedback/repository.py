"""Database access for customers and responses (Spring: JpaRepository).

Rules: only queries live here. No business decisions, no commits.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.feedback.models import Customer, Response


def find_customer_by_email(db: Session, email: str) -> Customer | None:
    # select(...).where(...) builds "SELECT * FROM customers WHERE email = ?".
    # db.scalar returns the first matching object, or None.
    return db.scalar(select(Customer).where(Customer.email == email))


def find_customer_by_phone(db: Session, phone: str) -> Customer | None:
    return db.scalar(select(Customer).where(Customer.phone == phone))


def save_customer(db: Session, customer: Customer) -> Customer:
    db.add(customer)  # marks it to be inserted; the service commits later
    return customer


def save_response(db: Session, response: Response) -> Response:
    db.add(response)
    db.flush()  # sends the INSERT now so response.id exists, WITHOUT ending the transaction
    return response


def find_response(db: Session, response_id: int) -> Response | None:
    # joinedload fetches the customer in the same SQL query (avoids one query per row).
    query = (
        select(Response).options(joinedload(Response.customer)).where(Response.id == response_id)
    )
    return db.scalar(query)


def list_responses(db: Session, limit: int, offset: int) -> list[Response]:
    """Newest first, one page at a time (limit = page size, offset = rows to skip)."""
    query = (
        select(Response)
        .options(joinedload(Response.customer))
        .order_by(Response.created_at.desc(), Response.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(query).all())
