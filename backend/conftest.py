"""Shared test setup. pytest loads this file automatically before running any test.

Fixtures are reusable "ingredients": a test asks for one by putting its name as a parameter,
and pytest builds it first.

Golden rules of these tests:
  * They use an in-memory SQLite database, so PostgreSQL is NOT needed.
  * Real email / SMS / AI are NEVER used: your .env keys are blanked below, and sending is
    replaced by lists that simply record what would have been sent.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.alerts import notifications
from app.core.config import get_settings
from app.core.database import Base, get_db
from app.main import app
from app.sms import client as sms_client
from app.sms.client import SmsResult


@pytest.fixture(autouse=True)  # autouse = applied to EVERY test automatically
def isolate_settings(monkeypatch):
    """Blank every secret so tests behave the same on any machine and never call real services.

    Environment variables win over the .env file, so setting them to "" hides your real keys.
    """
    for name in (
        "AI_API_KEY",
        "SMTP_HOST",
        "SMTP_USER",
        "SMTP_PASSWORD",
        "AT_API_KEY",
        "CARE_REP_PHONE",
    ):
        monkeypatch.setenv(name, "")
    get_settings.cache_clear()  # forget the cached Settings so the blanks take effect
    yield
    get_settings.cache_clear()  # and forget them again afterwards


@pytest.fixture()
def db_factory():
    """A fresh, empty, in-memory database for each test (returns a session factory)."""
    # StaticPool + check_same_thread=False: every connection shares the same in-memory database.
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)  # create all tables from the entity classes
    return sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture()
def sent_alerts():
    """Ids of alerts that WOULD have been emailed/texted to the care rep."""
    return []


@pytest.fixture()
def sent_sms():
    """(phone, text) pairs that WOULD have been sent."""
    return []


@pytest.fixture()
def client(db_factory, sent_alerts, sent_sms, monkeypatch):
    """A fake browser (TestClient) wired to the test database and fake senders."""

    def override_db():
        with db_factory() as session:
            yield session

    # Replace the real database dependency with the test database.
    app.dependency_overrides[get_db] = override_db
    # Replace the background "send email + SMS" job and the SMS sender with recorders.
    monkeypatch.setattr(notifications, "dispatch_alert", sent_alerts.append)
    monkeypatch.setattr(
        sms_client,
        "send_sms",
        lambda to, msg: sent_sms.append((to, msg)) or SmsResult(True, "fake ok"),
    )
    yield TestClient(app)
    app.dependency_overrides.clear()  # undo the replacement after the test


@pytest.fixture()
def make_payload():
    """Build a valid POST /api/feedback body. Override any field you want to change."""

    def build(**overrides):
        body = {
            "name": "Amina Otieno",
            "email": "amina@example.com",
            "phone": "+254712345678",
            "kind": "buyer",
            "product_rating": 5,
            "care_rating": 4,
            "happy_rating": 5,
        }
        return {**body, **overrides}  # later keys win, so overrides replace the defaults

    return build
