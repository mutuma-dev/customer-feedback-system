"""Tests for emailing and texting the care rep."""

from app.alerts import notifications
from app.alerts.models import Alert
from app.core.config import Settings
from app.feedback.models import Customer, Response
from app.sms import client as sms_client
from app.sms.client import SmsResult


def _make_alert(db_factory) -> int:
    """Helper: put one customer + response + alert in the test database; return the alert id."""
    with db_factory() as db:
        customer = Customer(
            name="Amina Otieno", email="amina@example.com", phone=None, kind="buyer"
        )
        response = Response(
            customer=customer,
            product_rating=1,
            care_rating=2,
            happy_rating=1,
            mean=1.33,
            category="detractor",
            source="web",
        )
        db.add(response)
        db.flush()
        alert = Alert(response_id=response.id)
        db.add(alert)
        db.commit()
        return alert.id


def test_email_body_contains_name_and_email():
    # The brief says the alert must carry the customer's name and email.
    customer = Customer(name="Amina Otieno", email="amina@example.com", phone="+254700000000")
    response = Response(product_rating=1, care_rating=2, happy_rating=1, mean=1.33, source="web")
    body = notifications.build_alert_email(customer, response)
    assert "Amina Otieno" in body
    assert "amina@example.com" in body


def test_send_email_without_smtp_only_logs(monkeypatch):
    monkeypatch.setattr(notifications, "get_settings", lambda: Settings(smtp_host=""))
    assert notifications.send_email("care@x.com", "Subject", "Body") is False


def test_send_email_uses_starttls_login_and_send(monkeypatch):
    calls = []  # records every step so we can check the ORDER

    class FakeSMTP:
        """A pretend mail server that only records what it is asked to do."""

        def __init__(self, host, port, timeout):
            calls.append(("connect", host, port))

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def starttls(self):
            calls.append("starttls")

        def login(self, user, password):
            calls.append(("login", user, password))

        def send_message(self, message):
            calls.append(("send", message["To"], message["Subject"]))

    settings = Settings(smtp_host="smtp.test", smtp_port=587, smtp_user="u", smtp_password="p")
    monkeypatch.setattr(notifications, "get_settings", lambda: settings)
    monkeypatch.setattr(notifications.smtplib, "SMTP", FakeSMTP)

    assert notifications.send_email("care@x.com", "Hello", "Body") is True
    assert calls == [
        ("connect", "smtp.test", 587),
        "starttls",
        ("login", "u", "p"),
        ("send", "care@x.com", "Hello"),
    ]


def test_send_email_failure_returns_false(monkeypatch):
    def broken(*args, **kwargs):
        raise OSError("no network")

    monkeypatch.setattr(notifications, "get_settings", lambda: Settings(smtp_host="smtp.test"))
    monkeypatch.setattr(notifications.smtplib, "SMTP", broken)
    # An email failure must be reported as False, never raised.
    assert notifications.send_email("care@x.com", "S", "B") is False


def test_dispatch_alert_records_what_was_delivered(db_factory, monkeypatch):
    alert_id = _make_alert(db_factory)
    texts = []
    settings = Settings(care_rep_email="care@x.com", care_rep_phone="+254711111111")
    monkeypatch.setattr(notifications, "get_settings", lambda: settings)
    monkeypatch.setattr(notifications, "send_email", lambda to, subject, body: True)
    monkeypatch.setattr(
        sms_client, "send_sms", lambda to, msg: texts.append((to, msg)) or SmsResult(True, "ok")
    )

    notifications.dispatch_alert(alert_id, session_factory=db_factory)

    with db_factory() as db:
        alert = db.get(Alert, alert_id)
        assert alert.email_sent is True
        assert alert.sms_sent is True
    assert texts[0][0] == "+254711111111"  # the SMS went to the care rep
    assert "Amina Otieno" in texts[0][1]


def test_dispatch_alert_without_care_phone_skips_sms(db_factory, monkeypatch):
    alert_id = _make_alert(db_factory)
    monkeypatch.setattr(notifications, "get_settings", lambda: Settings(care_rep_phone=""))
    monkeypatch.setattr(notifications, "send_email", lambda to, subject, body: False)

    notifications.dispatch_alert(alert_id, session_factory=db_factory)

    with db_factory() as db:
        alert = db.get(Alert, alert_id)
        assert alert.email_sent is False  # the failed email is recorded honestly
        assert alert.sms_sent is False  # no phone configured -> no SMS


def test_dispatch_unknown_alert_does_nothing(db_factory):
    notifications.dispatch_alert(999, session_factory=db_factory)  # must not raise an error
