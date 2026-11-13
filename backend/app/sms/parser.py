"""Reads a painter's SMS reply such as "4 5 4"."""

import re

# A "regular expression": a pattern for matching text.
#   ^ and $        = the whole message must match, not just a part
#   \s*            = optional spaces
#   ([1-5])        = one digit from 1 to 5, captured so we can read it
#   [\s,.\-]*      = optionally separated by spaces, commas, dots or dashes
# So "4 5 4", "454", "4,5,4" and "4-5-4" all match; "4 5 6" and "hello" do not.
_RATINGS = re.compile(r"^\s*([1-5])[\s,.\-]*([1-5])[\s,.\-]*([1-5])\s*$")


def parse_ratings(text: str) -> tuple[int, int, int] | None:
    """Return (product, care, happy) or None if the text is not three valid ratings."""
    match = _RATINGS.match(text)
    if match is None:
        return None
    a, b, c = match.groups()  # the three captured digits (as text)
    return int(a), int(b), int(c)
