"""Turns three ratings into a verdict.

Pure functions (no database, no network), so they are very easy to test.
"""

from typing import Literal

# Literal means "only these three exact strings are allowed".
Category = Literal["detractor", "passive", "promoter"]


def classify(product: int, care: int, happy: int) -> tuple[float, Category]:
    """Return (mean rounded to 2 decimals, category).

    The brief's rule: mean < 3 detractor, mean == 3 passive, mean > 3 promoter.

    We compare the integer SUM with 9 instead of comparing a decimal mean with 3,
    because decimals can be slightly inexact (2.9999999). sum < 9 is the same as mean < 3.
    """
    total = product + care + happy
    mean = round(total / 3, 2)
    if total < 9:
        return mean, "detractor"
    if total == 9:
        return mean, "passive"
    return mean, "promoter"
