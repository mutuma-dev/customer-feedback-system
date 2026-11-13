"""One definition of "now" so every timestamp is timezone-aware UTC."""

from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)
