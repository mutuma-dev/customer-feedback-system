"""Sends SMS through Africa's Talking (Spring: a client / gateway class).

Africa's Talking has a "sandbox" for testing: messages show up in their simulator,
NOT on real phones.

IMPORTANT: Africa's Talking answers "HTTP 201 Created" even when it refuses to deliver to a
recipient (bad sender id, bad number, no balance...). The real verdict is inside the JSON reply,
in "Recipients". This file reads it, so "sent" really means "accepted for delivery".
"""

import logging
from dataclasses import dataclass

import httpx  # a library for making HTTP calls to other websites

from app.core.config import get_settings

log = logging.getLogger(__name__)

SANDBOX_URL = "https://api.sandbox.africastalking.com/version1/messaging"
LIVE_URL = "https://api.africastalking.com/version1/messaging"

# Africa's Talking per-recipient status codes that mean "accepted": 100 processed, 101 sent,
# 102 queued. Anything else (402 InvalidSenderId, 403 InvalidPhoneNumber, 405 InsufficientBalance,
# 407 CouldNotRoute ...) means the message was NOT delivered.
ACCEPTED_CODES = {100, 101, 102}


@dataclass
class SmsResult:
    """The outcome of one send attempt."""

    ok: bool  # True = accepted for delivery
    detail: str  # a human-readable reason, shown in /docs and in the log


def interpret_response(data: dict) -> SmsResult:
    """Turn Africa's Talking's JSON reply into an SmsResult (pure function, easy to test)."""
    message_data = data.get("SMSMessageData", {})
    recipients = message_data.get("Recipients") or []
    if not recipients:
        # No recipient was accepted. The reason is usually in the general message,
        # e.g. "InvalidSenderId".
        reason = message_data.get("Message") or "Africa's Talking returned no recipients"
        return SmsResult(False, f"Not sent: {reason}")

    first = recipients[0]
    code = first.get("statusCode")
    status = first.get("status", "unknown")
    if code in ACCEPTED_CODES or status == "Success":
        return SmsResult(True, f"Accepted by Africa's Talking: {status} (code {code})")
    return SmsResult(False, f"Africa's Talking refused it: {status} (code {code})")


def send_sms(to: str, message: str) -> SmsResult:
    """Send one SMS and say what happened.

    It NEVER raises an error: a failed SMS must not break the request that triggered it.
    """
    settings = get_settings()
    if not settings.at_api_key:
        # Not configured: just show what would have been sent (handy during development).
        log.info("SMS not configured; would send to %s: %s", to, message)
        return SmsResult(False, "Not sent: AT_API_KEY is empty in .env")

    is_sandbox = settings.at_username == "sandbox"
    url = SANDBOX_URL if is_sandbox else LIVE_URL
    data = {"username": settings.at_username, "to": to, "message": message}
    if settings.at_sender_id and not is_sandbox:
        # A sender id must be REGISTERED with Africa's Talking, and the sandbox does not use one.
        # Sending an unregistered sender id (like the word "sandbox") makes them refuse the SMS.
        data["from"] = settings.at_sender_id
    elif settings.at_sender_id:
        log.info("Ignoring AT_SENDER_ID in sandbox mode (sandbox has no sender ids)")
    try:
        response = httpx.post(
            url,
            headers={"apiKey": settings.at_api_key, "Accept": "application/json"},
            data=data,  # form-encoded body, which is what Africa's Talking expects
            timeout=10,  # give up after 10 seconds instead of waiting forever
        )
        response.raise_for_status()  # HTTP errors such as 401 (wrong API key) become exceptions
        result = interpret_response(response.json())
    except httpx.HTTPStatusError as error:
        body = error.response.text[:200] if error.response is not None else ""
        result = SmsResult(False, f"Africa's Talking error {error.response.status_code}: {body}")
    except Exception as error:
        result = SmsResult(False, f"Could not reach Africa's Talking: {error}")

    # The terminal now always shows the true outcome.
    (log.info if result.ok else log.warning)("SMS to %s: %s", to, result.detail)
    return result
