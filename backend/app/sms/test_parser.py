"""Tests for reading painters' SMS replies."""

import pytest

from app.sms.parser import parse_ratings


# parametrize runs the same test once for each value in the list.
@pytest.mark.parametrize("text", ["4 5 4", "454", " 4,5,4 ", "4-5-4", "4.5.4"])
def test_valid_replies(text):
    assert parse_ratings(text) == (4, 5, 4)


@pytest.mark.parametrize(
    "text", ["", "hello", "4 5", "4 5 6", "0 1 2", "4 5 4 3", "four five four"]
)
def test_invalid_replies(text):
    assert parse_ratings(text) is None
