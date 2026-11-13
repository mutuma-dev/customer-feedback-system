from sqlalchemy import func, select

from app.alerts.models import Alert
from app.feedback.models import Customer, Response
from app.seed import seed


def test_seed_creates_demo_data(db_factory):
    with db_factory() as db:
        assert seed(db) is True
        responses = db.scalar(select(func.count(Response.id)))
        assert 45 <= responses <= 105  # 15 days x 3-7 per day
        assert db.scalar(select(func.count(Customer.id))) == responses
        detractors = db.scalar(
            select(func.count(Response.id)).where(Response.category == "detractor")
        )
        assert db.scalar(select(func.count(Alert.id))) == detractors


def test_seed_is_idempotent(db_factory):
    with db_factory() as db:
        assert seed(db) is True
        before = db.scalar(select(func.count(Response.id)))
        assert seed(db) is False  # second run does nothing
        assert db.scalar(select(func.count(Response.id))) == before
