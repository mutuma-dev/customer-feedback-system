"""Fill the database with demo data:  python -m app.seed"""

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.alerts.models import Alert
from app.core.database import SessionLocal
from app.feedback.models import Customer, Response
from app.feedback.scoring import classify

# Name pieces used to invent customers.
FIRST = [
    "Amina",
    "Brian",
    "Cynthia",
    "David",
    "Esther",
    "Felix",
    "Grace",
    "Hassan",
    "Irene",
    "John",
]
LAST = ["Otieno", "Mwangi", "Wanjiku", "Kamau", "Achieng", "Njoroge", "Mutua", "Barasa"]


def seed(db: Session) -> bool:
    """Insert about 70 demo responses over 15 days. Returns False if data already exists."""
    if db.scalar(select(func.count(Response.id))):
        return False  # never duplicate data

    rng = random.Random(42)  # a fixed seed makes the "random" data identical on every run
    now = datetime.now(timezone.utc)
    for days_ago in range(14, -1, -1):  # 14 days ago ... today
        for i in range(rng.randint(3, 7)):  # 3 to 7 customers each day
            name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
            kind = "painter" if rng.random() < 0.3 else "buyer"  # about 30% painters
            customer = Customer(
                name=name,
                email=f"{name.lower().replace(' ', '.')}.{days_ago}{i}@example.com",
                phone=f"+2547{rng.randint(10000000, 99999999)}",
                kind=kind,
            )
            # Satisfaction improves slowly over the two weeks so the trend line has a story.
            bias = 3.2 + (14 - days_ago) * 0.04
            # gauss = bell curve around `bias`; each rating is rounded and kept within 1-5.
            ratings = tuple(min(5, max(1, round(rng.gauss(bias, 1.1)))) for _ in range(3))
            mean, category = classify(*ratings)
            created = now - timedelta(days=days_ago, hours=rng.randint(0, 10))
            response = Response(
                customer=customer,
                product_rating=ratings[0],
                care_rating=ratings[1],
                happy_rating=ratings[2],
                mean=mean,
                category=category,
                source="sms" if kind == "painter" else "web",  # painters answer by SMS
                created_at=created,
            )
            db.add(response)
            db.flush()  # get response.id
            if category == "detractor":
                # Alerts older than 5 days are already read; recent ones are unread,
                # so the dashboard bell shows a number badge as soon as you open it.
                db.add(Alert(response_id=response.id, created_at=created, is_read=days_ago > 5))
    db.commit()
    return True


def main() -> None:
    with SessionLocal() as db:
        print("Seeded demo data." if seed(db) else "Database already has responses; skipping seed.")


if __name__ == "__main__":
    main()
