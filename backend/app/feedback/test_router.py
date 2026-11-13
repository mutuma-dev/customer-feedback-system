from sqlalchemy import func, select

from app.feedback.models import Customer


def test_promoter_creates_no_alert(client, make_payload, sent_alerts):
    response = client.post("/api/feedback", json=make_payload())
    assert response.status_code == 201
    assert response.json()["category"] == "promoter"
    assert response.json()["alert_created"] is False
    assert sent_alerts == []


def test_detractor_creates_alert_and_triggers_notification(client, make_payload, sent_alerts):
    body = make_payload(product_rating=2, care_rating=3, happy_rating=2, email="b@example.com")
    response = client.post("/api/feedback", json=body)
    assert response.json() == {
        "id": 1,
        "mean": 2.33,
        "category": "detractor",
        "alert_created": True,
    }
    assert sent_alerts == [1]


def test_rating_out_of_range_is_rejected(client, make_payload):
    assert client.post("/api/feedback", json=make_payload(care_rating=6)).status_code == 422
    assert client.post("/api/feedback", json=make_payload(care_rating=0)).status_code == 422


def test_invalid_email_is_rejected(client, make_payload):
    assert client.post("/api/feedback", json=make_payload(email="not-an-email")).status_code == 422


def test_missing_name_is_rejected(client, make_payload):
    assert client.post("/api/feedback", json=make_payload(name="")).status_code == 422


def test_same_email_reuses_the_customer(client, make_payload, db_factory):
    client.post("/api/feedback", json=make_payload())
    client.post("/api/feedback", json=make_payload(care_rating=2))
    with db_factory() as db:
        assert db.scalar(select(func.count(Customer.id))) == 1
