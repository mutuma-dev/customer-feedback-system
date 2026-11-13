"""Fill the database with demo data: python -m app.seed"""

import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.alerts.models import Alert
from app.core.database import SessionLocal
from app.feedback.models import Customer, Response
from app.feedback.scoring import classify

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
    """Insert ~75 demo responses over 15 days. Returns False if data already exists."""
    if db.scalar(select(func.count(Response.id))):
        return False

    rng = random.Random(42)  # fixed seed: the same demo data every time
    now = datetime.now(timezone.utc)
    for days_ago in range(14, -1, -1):
        for i in range(rng.randint(3, 7)):
            name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
            kind = "painter" if rng.random() < 0.3 else "buyer"
            customer = Customer(
                name=name,
                email=f"{name.lower().replace(' ', '.')}.{days_ago}{i}@example.com",
                phone=f"+2547{rng.randint(10000000, 99999999)}",
                kind=kind,
            )
            # Satisfaction improves slowly over the two weeks so the trend line has a story.
            bias = 3.2 + (14 - days_ago) * 0.04
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
                source="sms" if kind == "painter" else "web",
                created_at=created,
            )
            db.add(response)
            db.flush()
            if category == "detractor":
                db.add(Alert(response_id=response.id, created_at=created, is_read=days_ago > 2))
    db.commit()
    return True


def main() -> None:
    with SessionLocal() as db:
        print("Seeded demo data." if seed(db) else "Database already has responses; skipping seed.")


if __name__ == "__main__":
    main()
