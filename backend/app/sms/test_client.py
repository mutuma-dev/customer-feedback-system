"""Tests for the Africa's Talking client: reading its real answer, sandbox rules, failures."""

import httpx

from app.core.config import Settings
from app.sms import client
from app.sms.client import SmsResult, interpret_response


class FakeResponse:
    """Stands in for the HTTP answer from Africa's Talking."""

    def __init__(self, payload, status=201):
        self._payload, self.status_code = payload, status
        self.text = str(payload)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("bad", request=None, response=self)  # type: ignore[arg-type]

    def json(self):
        return self._payload


def _answer(code, status):
    """A reply shaped like Africa's Talking's, with one recipient."""
    return {
        "SMSMessageData": {"Message": "x", "Recipients": [{"statusCode": code, "status": status}]}
    }


def test_success_codes_are_accepted():
    for code in (100, 101, 102):
        assert interpret_response(_answer(code, "Success")).ok is True


def test_refused_recipient_is_not_reported_as_sent():
    # HTTP 201 but the recipient was refused (bad sender id): must NOT count as sent.
    result = interpret_response(_answer(402, "InvalidSenderId"))
    assert result.ok is False
    assert "InvalidSenderId" in result.detail


def test_empty_recipients_use_the_general_message():
    result = interpret_response(
        {"SMSMessageData": {"Message": "InvalidSenderId", "Recipients": []}}
    )
    assert result.ok is False
    assert "InvalidSenderId" in result.detail


def test_without_an_api_key_nothing_is_sent():
    result = client.send_sms("+254700000000", "hi")  # tests blank the key (see conftest)
    assert result == SmsResult(False, "Not sent: AT_API_KEY is empty in .env")


def _configure(monkeypatch, **settings):
    seen = {}

    def fake_post(url, headers, data, timeout):
        seen.update(url=url, headers=headers, data=data)
        return FakeResponse(_answer(101, "Success"))

    monkeypatch.setattr(client, "get_settings", lambda: Settings(at_api_key="key", **settings))
    monkeypatch.setattr(client.httpx, "post", fake_post)
    return seen


def test_sandbox_uses_the_sandbox_url_and_ignores_the_sender_id(monkeypatch):
    seen = _configure(monkeypatch, at_username="sandbox", at_sender_id="sandbox")
    assert client.send_sms("+254700000000", "hi").ok is True
    assert "sandbox" in seen["url"]
    assert "from" not in seen["data"]  # the sender id is NOT sent in sandbox mode
    assert seen["headers"]["apiKey"] == "key"


def test_live_mode_sends_the_registered_sender_id(monkeypatch):
    seen = _configure(monkeypatch, at_username="mycompany", at_sender_id="COMPANYX")
    client.send_sms("+254700000000", "hi")
    assert "sandbox" not in seen["url"]
    assert seen["data"]["from"] == "COMPANYX"


def test_wrong_api_key_is_reported(monkeypatch):
    monkeypatch.setattr(client, "get_settings", lambda: Settings(at_api_key="bad"))
    monkeypatch.setattr(client.httpx, "post", lambda *a, **k: FakeResponse("invalid auth", 401))
    result = client.send_sms("+254700000000", "hi")
    assert result.ok is False
    assert "401" in result.detail


def test_network_failure_is_reported_not_raised(monkeypatch):
    def broken(*args, **kwargs):
        raise httpx.ConnectError("no internet")

    monkeypatch.setattr(client, "get_settings", lambda: Settings(at_api_key="key"))
    monkeypatch.setattr(client.httpx, "post", broken)
    result = client.send_sms("+254700000000", "hi")
    assert result.ok is False
    assert "Could not reach" in result.detail
