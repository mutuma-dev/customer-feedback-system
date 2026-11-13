"""Tests for the trend projection maths."""

from datetime import date, timedelta

from app.dashboard.analytics import linear_projection


def test_projection_needs_two_points():
    assert linear_projection([(date(2026, 1, 1), 3.0)]) == []
    assert linear_projection([]) == []


def test_projection_follows_the_slope():
    start = date(2026, 1, 1)
    points = [(start + timedelta(days=i), 2.0 + 0.25 * i) for i in range(4)]  # 2.0 ... 2.75
    result = linear_projection(points, horizon=3)
    assert [d for d, _ in result] == [start + timedelta(days=i) for i in (4, 5, 6)]
    assert [m for _, m in result] == [3.0, 3.25, 3.5]  # the line simply continues


def test_projection_is_clamped_to_the_scale():
    start = date(2026, 1, 1)
    rising = [(start + timedelta(days=i), 3.0 + 0.5 * i) for i in range(4)]
    assert linear_projection(rising, horizon=3)[-1][1] == 5.0  # never above 5
    falling = [(start + timedelta(days=i), 3.0 - 0.5 * i) for i in range(4)]
    assert linear_projection(falling, horizon=3)[-1][1] == 1.0  # never below 1


def test_flat_data_gives_flat_projection():
    start = date(2026, 1, 1)
    flat = [(start + timedelta(days=i), 4.0) for i in range(3)]
    assert {m for _, m in linear_projection(flat)} == {4.0}


def test_gaps_between_days_are_respected():
    # Day 0 -> 1.0 and day 10 -> 3.0: slope 0.2 per day, so day 11 is 3.2.
    points = [(date(2026, 1, 1), 1.0), (date(2026, 1, 11), 3.0)]
    assert linear_projection(points, horizon=1)[0][1] == 3.2
