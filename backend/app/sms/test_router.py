"""Tests for the SMS endpoints (invite + incoming webhook)."""

from app.sms.messages import HELP_TEXT, INVITE_TEXT, THANKS_TEXT


def test_valid_reply_is_saved_and_thanked(client, sent_sms, sent_alerts):
    response = client.post("/api/sms/incoming", data={"from": "+254700000001", "text": "5 5 4"})
    assert response.json() == {"status": "saved"}
    saved = client.get("/api/responses").json()[0]
    assert saved["source"] == "sms"
    assert saved["customer"]["kind"] == "painter"
    assert saved["category"] == "promoter"
    assert sent_sms == [("+254700000001", THANKS_TEXT)]  # a thank-you text goes back
    assert sent_alerts == []  # happy painter: no alert


def test_unhappy_reply_raises_an_alert(client, sent_alerts):
    client.post("/api/sms/incoming", data={"from": "+254700000001", "text": "1 2 1"})
    assert sent_alerts == [1]


def test_garbage_reply_gets_help_and_is_not_saved(client, sent_sms):
    response = client.post(
        "/api/sms/incoming", data={"from": "+254700000002", "text": "great paint!"}
    )
    assert response.json() == {"status": "ignored"}
    assert client.get("/api/stats").json()["total"] == 0  # nothing saved
    assert sent_sms == [("+254700000002", HELP_TEXT)]


def test_sender_is_normalised_to_e164(client):
    # Form encoding can drop the "+", so the app adds it back.
    client.post("/api/sms/incoming", data={"from": "254700000003", "text": "5 5 5"})
    assert client.get("/api/responses").json()[0]["customer"]["phone"] == "+254700000003"


def test_invite_sends_the_brief_message(client, sent_sms):
    response = client.post("/api/sms/invite", json={"phone": "+254 711 000 111"})
    assert response.json() == {"sent": True}
    assert sent_sms == [("+254711000111", INVITE_TEXT)]  # spaces were removed


def test_invite_rejects_short_numbers(client):
    assert client.post("/api/sms/invite", json={"phone": "123"}).status_code == 422
