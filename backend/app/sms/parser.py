"""Reads a painter's reply such as "4 5 4"."""

import re

# Three digits 1-5, optionally separated by spaces, commas, dots or dashes ("454", "4 5 4").
_RATINGS = re.compile(r"^\s*([1-5])[\s,.\-]*([1-5])[\s,.\-]*([1-5])\s*$")


def parse_ratings(text: str) -> tuple[int, int, int] | None:
    """Return (product, care, happy) or None if the text is not three valid ratings."""
    match = _RATINGS.match(text)
    if match is None:
        return None
    a, b, c = match.groups()
    return int(a), int(b), int(c)
