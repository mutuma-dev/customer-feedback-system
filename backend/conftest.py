"""Shared test fixtures (pytest finds this file automatically).

Tests run on an in-memory SQLite database, so you do NOT need PostgreSQL to run them.
Real email/SMS sending is replaced by lists that record what would have been sent.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.alerts import notifications
from app.core.database import Base, get_db
from app.main import app
from app.sms import client as sms_client


@pytest.fixture()
def db_factory():
    """A fresh empty database for each test."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture()
def sent_alerts():
    """alert ids that would have been emailed/texted to the care rep"""
    return []


@pytest.fixture()
def sent_sms():
    """(phone, text) pairs that would have been sent"""
    return []


@pytest.fixture()
def client(db_factory, sent_alerts, sent_sms, monkeypatch):
    def override_db():
        with db_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    monkeypatch.setattr(notifications, "dispatch_alert", sent_alerts.append)
    monkeypatch.setattr(sms_client, "send_sms", lambda to, msg: sent_sms.append((to, msg)) or True)
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def make_payload():
    """Build a valid POST /api/feedback body; override any field you want to change."""

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
        return {**body, **overrides}

    return build
