"""Sends SMS through Africa's Talking (Spring: a client / gateway class).

Africa's Talking has a "sandbox" for testing: messages show up in their simulator,
not on real phones.
"""

import logging

import httpx  # a library for making HTTP calls to other websites

from app.core.config import get_settings

log = logging.getLogger(__name__)  # a logger named after this file; prints to the terminal

SANDBOX_URL = "https://api.sandbox.africastalking.com/version1/messaging"
LIVE_URL = "https://api.africastalking.com/version1/messaging"


def send_sms(to: str, message: str) -> bool:
    """Send one SMS. Returns True on success.

    It NEVER raises an error: a failed SMS must not break the request that triggered it.
    """
    settings = get_settings()
    if not settings.at_api_key:
        log.info("SMS not configured; would send to %s: %s", to, message)
        return False

    # Username "sandbox" means "use the test environment".
    url = SANDBOX_URL if settings.at_username == "sandbox" else LIVE_URL
    data = {"username": settings.at_username, "to": to, "message": message}
    if settings.at_sender_id:
        data["from"] = settings.at_sender_id
    try:
        response = httpx.post(
            url,
            headers={"apiKey": settings.at_api_key, "Accept": "application/json"},
            data=data,  # form-encoded body, which is what Africa's Talking expects
            timeout=10,  # give up after 10 seconds instead of waiting forever
        )
        response.raise_for_status()  # turns HTTP errors (401, 500 ...) into exceptions
        return True
    except Exception:
        log.exception("SMS to %s failed", to)  # logs the full error with its stack trace
        return False
