def _detractor(client, make_payload):
    client.post(
        "/api/feedback",
        json=make_payload(product_rating=1, care_rating=1, happy_rating=1),
    )


def test_list_alerts_includes_customer_contact(client, make_payload):
    _detractor(client, make_payload)
    alerts = client.get("/api/alerts").json()
    assert len(alerts) == 1
    assert alerts[0]["response"]["customer"]["email"] == "amina@example.com"
    assert alerts[0]["is_read"] is False


def test_unread_filter(client, make_payload):
    _detractor(client, make_payload)
    client.post("/api/alerts/1/read")
    assert client.get("/api/alerts?unread_only=true").json() == []
    assert len(client.get("/api/alerts").json()) == 1


def test_mark_read(client, make_payload):
    _detractor(client, make_payload)
    assert client.post("/api/alerts/1/read").json()["is_read"] is True


def test_draft_reply_uses_template_without_ai_key(client, make_payload):
    _detractor(client, make_payload)
    result = client.post("/api/alerts/1/draft-reply").json()
    assert result["ai_used"] is False
    assert "Amina" in result["draft"]
    # the draft is remembered on the alert
    assert client.get("/api/alerts").json()[0]["draft_reply"] == result["draft"]


def test_unknown_alert_is_404(client):
    assert client.post("/api/alerts/99/read").status_code == 404
    assert client.post("/api/alerts/99/draft-reply").status_code == 404
