"""Trend projection: a straight line fitted through the daily average scores."""

from datetime import date, timedelta


def linear_projection(
    points: list[tuple[date, float]], horizon: int = 7
) -> list[tuple[date, float]]:
    """Fit y = a + b*x by least squares (x = day number) and extend it `horizon` days.

    Needs at least 2 days of data, otherwise returns []. Results are clamped to the 1-5 scale.
    """
    if len(points) < 2:
        return []

    xs = [d.toordinal() for d, _ in points]
    ys = [m for _, m in points]
    n = len(points)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n

    denominator = sum((x - mean_x) ** 2 for x in xs)
    if denominator == 0:
        slope = 0.0
    else:
        slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True)) / denominator
    intercept = mean_y - slope * mean_x

    last_day = points[-1][0]
    result = []
    for i in range(1, horizon + 1):
        day = last_day + timedelta(days=i)
        value = intercept + slope * day.toordinal()
        result.append((day, round(min(5.0, max(1.0, value)), 2)))
    return result
