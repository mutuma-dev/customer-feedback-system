"""AI touch: draft a polite follow-up email for an unhappy customer.
"""

import logging

import httpx

from app.core.config import get_settings

log = logging.getLogger(__name__)

# The instructions given to the AI model.
SYSTEM_PROMPT = (
    "You write short, warm, professional follow-up emails for the customer care team of "
    "Company X, a paint seller. The customer just gave low ratings. Apologise sincerely, "
    "acknowledge the weak area, offer to help and ask how we can make it right. "
    "Maximum 90 words. Do not invent discounts, promises or facts. "
    "Sign off as 'Company X Care Team'."
)


def fallback_draft(first_name: str) -> str:
    """The built-in template used when there is no AI key or the AI call fails."""
    return (
        f"Hi {first_name},\n\n"
        "Thank you for your feedback. We're sorry your experience with Company X did not "
        "meet your expectations. We would like to put this right - could you tell us more "
        "about what went wrong, or reply with a good time for a quick call?\n\n"
        "Kind regards,\nCompany X Care Team"
    )


def draft_reply(name: str, product: int, care: int, happy: int) -> tuple[str, bool]:
    """Return (draft text, ai_used).

    Privacy: only the FIRST NAME and the three ratings are sent to the AI provider.
    The surname, email and phone number never leave our server.
    """
    settings = get_settings()
    first_name = name.split()[0] if name.strip() else "there"
    if not settings.ai_api_key:
        return fallback_draft(first_name), False

    # The "user message": the facts the AI should write about.
    prompt = (
        f"Customer first name: {first_name}\n"
        f"Product rating: {product}/5\nCustomer care rating: {care}/5\n"
        f"Happiness with product: {happy}/5\nWrite the email body only."
    )
    try:
        response = httpx.post(
            f"{settings.ai_base_url.rstrip('/')}/chat/completions",
            headers={"Authorization": f"Bearer {settings.ai_api_key}"},
            json={
                "model": settings.ai_model,
                "max_tokens": 300,  # cap the length of the answer
                "temperature": 0.4,  # low = calm and consistent wording
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=settings.ai_timeout_seconds,  # never wait longer than this
        )
        response.raise_for_status()
        # The answer text lives at choices[0].message.content in this format.
        text = (response.json()["choices"][0]["message"]["content"] or "").strip()
        if text:
            return text, True
    except Exception:
        log.exception("AI draft failed; using template")
    # No key, an error, a timeout or an empty answer all end up here.
    return fallback_draft(first_name), False
