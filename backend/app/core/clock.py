"""One definition of "now", so every timestamp is timezone-aware UTC."""

from datetime import datetime, timezone


def utcnow() -> datetime:
    """Current time in UTC. Used as the default value of every created_at column."""
    return datetime.now(timezone.utc)
