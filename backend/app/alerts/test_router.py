"""Tests for the alert endpoints."""


def _detractor(client, make_payload):
    """Helper: submit a very unhappy survey so that an alert exists."""
    client.post("/api/feedback", json=make_payload(product_rating=1, care_rating=1, happy_rating=1))


def test_list_alerts_includes_customer_contact(client, make_payload):
    _detractor(client, make_payload)
    alerts = client.get("/api/alerts").json()
    assert len(alerts) == 1
    assert alerts[0]["response"]["customer"]["email"] == "amina@example.com"
    assert alerts[0]["is_read"] is False  # new alerts start unread


def test_unread_filter(client, make_payload):
    _detractor(client, make_payload)
    client.post("/api/alerts/1/read")
    assert client.get("/api/alerts?unread_only=true").json() == []  # none unread now
    assert len(client.get("/api/alerts").json()) == 1  # but it still exists


def test_mark_read(client, make_payload):
    _detractor(client, make_payload)
    assert client.post("/api/alerts/1/read").json()["is_read"] is True


def test_mark_all_read_changes_only_unread_alerts(client, make_payload):
    # Two unhappy customers -> two unread alerts.
    client.post("/api/feedback", json=make_payload(product_rating=1, care_rating=1, happy_rating=1))
    client.post(
        "/api/feedback",
        json=make_payload(
            email="b@x.com", phone=None, product_rating=2, care_rating=1, happy_rating=1
        ),
    )
    client.post("/api/alerts/1/read")  # one is already read
    assert client.post("/api/alerts/read-all").json() == {"updated": 1}
    assert client.get("/api/alerts?unread_only=true").json() == []
    # Running it again changes nothing.
    assert client.post("/api/alerts/read-all").json() == {"updated": 0}


def test_draft_reply_uses_template_without_ai_key(client, make_payload):
    _detractor(client, make_payload)
    result = client.post("/api/alerts/1/draft-reply").json()
    assert result["ai_used"] is False  # no key during tests -> template
    assert "Amina" in result["draft"]
    # The draft is remembered on the alert.
    assert client.get("/api/alerts").json()[0]["draft_reply"] == result["draft"]


def test_unknown_alert_is_404(client):
    assert client.post("/api/alerts/99/read").status_code == 404
    assert client.post("/api/alerts/99/draft-reply").status_code == 404
