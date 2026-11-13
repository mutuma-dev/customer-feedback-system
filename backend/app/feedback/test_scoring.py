"""Tests for the scoring rule (pure logic, no database)."""

from app.feedback.scoring import classify


def test_brief_example_is_detractor():
    # The brief's own example: (2 + 3 + 2) / 3 = 2.33 -> detractor.
    assert classify(2, 3, 2) == (2.33, "detractor")


def test_exact_three_is_passive():
    # Only an exact 3.00 is passive, however the ratings are mixed.
    assert classify(3, 3, 3) == (3.0, "passive")
    assert classify(1, 4, 4) == (3.0, "passive")


def test_above_three_is_promoter():
    assert classify(4, 3, 3) == (3.33, "promoter")
    assert classify(5, 5, 5) == (5.0, "promoter")


def test_lowest_possible_is_detractor():
    assert classify(1, 1, 1) == (1.0, "detractor")
