"""Tests for settings parsing."""

from app.core.config import Settings


def test_cors_origins_are_split_and_trimmed():
    # Two addresses separated by a comma and a space become a clean list.
    settings = Settings(frontend_origin="http://localhost:3000, http://127.0.0.1:3000")
    assert settings.cors_origins == ["http://localhost:3000", "http://127.0.0.1:3000"]


def test_cors_ignores_empty_entries():
    # A trailing comma must not produce an empty origin.
    assert Settings(frontend_origin="http://a.com,,").cors_origins == ["http://a.com"]
