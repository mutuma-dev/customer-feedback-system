"""Sends SMS through Africa's Talking (Spring: a client/gateway class)."""

import logging

import httpx

from app.core.config import get_settings

log = logging.getLogger(__name__)

SANDBOX_URL = "https://api.sandbox.africastalking.com/version1/messaging"
LIVE_URL = "https://api.africastalking.com/version1/messaging"


def send_sms(to: str, message: str) -> bool:
    """Send one SMS. Returns True on success. Never raises: a failed SMS must not break the app."""
    settings = get_settings()
    if not settings.at_api_key:
        log.info("SMS not configured; would send to %s: %s", to, message)
        return False

    url = SANDBOX_URL if settings.at_username == "sandbox" else LIVE_URL
    data = {"username": settings.at_username, "to": to, "message": message}
    if settings.at_sender_id:
        data["from"] = settings.at_sender_id
    try:
        response = httpx.post(
            url,
            headers={"apiKey": settings.at_api_key, "Accept": "application/json"},
            data=data,
            timeout=10,
        )
        response.raise_for_status()
        return True
    except Exception:
        log.exception("SMS to %s failed", to)
        return False
