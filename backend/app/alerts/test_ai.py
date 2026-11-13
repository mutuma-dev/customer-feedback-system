"""Tests for the AI draft: success, every failure mode, and privacy."""

import httpx

from app.alerts import ai
from app.core.config import Settings


class FakeResponse:
    """Stands in for the HTTP response returned by the AI provider."""

    def __init__(self, payload, fail=False):
        self._payload, self._fail = payload, fail

    def raise_for_status(self):
        if self._fail:
            raise httpx.HTTPStatusError("boom", request=None, response=None)  # type: ignore[arg-type]

    def json(self):
        return self._payload


def _with_key(monkeypatch):
    """Make the AI module believe an API key is configured."""
    monkeypatch.setattr(ai, "get_settings", lambda: Settings(ai_api_key="test-key"))


def test_no_key_returns_template(monkeypatch):
    monkeypatch.setattr(ai, "get_settings", lambda: Settings(ai_api_key=""))
    draft, used = ai.draft_reply("Amina Otieno", 1, 2, 1)
    assert used is False
    assert draft.startswith("Hi Amina")


def test_successful_ai_call_is_used(monkeypatch):
    _with_key(monkeypatch)
    seen = {}

    def fake_post(url, headers, json, timeout):
        seen.update(url=url, headers=headers, json=json)  # remember what we sent
        return FakeResponse({"choices": [{"message": {"content": "  Dear Amina, sorry!  "}}]})

    monkeypatch.setattr(ai.httpx, "post", fake_post)
    draft, used = ai.draft_reply("Amina Otieno", 1, 2, 1)
    assert (draft, used) == ("Dear Amina, sorry!", True)  # whitespace is trimmed
    assert seen["url"].endswith("/chat/completions")
    assert seen["headers"]["Authorization"] == "Bearer test-key"
    assert seen["json"]["max_tokens"] >= 1000  # enough room for reasoning models
    # Privacy: only the first name and ratings are sent, never the surname.
    prompt = seen["json"]["messages"][1]["content"]
    assert "Amina" in prompt and "Otieno" not in prompt


def test_ai_failure_falls_back_to_template(monkeypatch):
    _with_key(monkeypatch)
    monkeypatch.setattr(ai.httpx, "post", lambda *a, **k: FakeResponse({}, fail=True))
    draft, used = ai.draft_reply("Amina", 1, 1, 1)
    assert used is False
    assert "Company X Care Team" in draft


def test_empty_ai_answer_falls_back(monkeypatch):
    _with_key(monkeypatch)
    monkeypatch.setattr(
        ai.httpx, "post", lambda *a, **k: FakeResponse({"choices": [{"message": {"content": ""}}]})
    )
    assert ai.draft_reply("Amina", 1, 1, 1)[1] is False
