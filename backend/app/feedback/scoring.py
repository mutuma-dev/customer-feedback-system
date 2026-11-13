"""Turns three ratings into a verdict. Pure functions: no database, easy to test."""

from typing import Literal

Category = Literal["detractor", "passive", "promoter"]


def classify(product: int, care: int, happy: int) -> tuple[float, Category]:
    """Return (mean rounded to 2 decimals, category).

    We compare the integer SUM with 9 instead of comparing the float mean with 3.
    That avoids floating point surprises: sum < 9 means mean < 3, sum == 9 means mean == 3.
    """
    total = product + care + happy
    mean = round(total / 3, 2)
    if total < 9:
        return mean, "detractor"
    if total == 9:
        return mean, "passive"
    return mean, "promoter"
