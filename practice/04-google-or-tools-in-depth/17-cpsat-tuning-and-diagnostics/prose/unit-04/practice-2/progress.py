from __future__ import annotations

import re

EVENT = re.compile(r"^#(\d+|Bound|Done)\s+\S+\s*(.*)$")
RANGE = re.compile(r"best:(\S+)\s+next:\[(\S+),(\S+)\]\s*(\S*)")


def number(text: str) -> int | None:
    return None if "inf" in text else int(text)


def events(log: str) -> list[tuple[str, int | None, int | None, str]]:
    """(kind, best, bound, worker) per progress line of a maximization; kind is solution, bound or done."""
    # TODO: one tuple per #N, #Bound and #Done line.
    return []


def stopped_by_a_limit(log: str) -> bool:
    """True if the search never reached its #Done line."""
    return False


if __name__ == "__main__":
    print(events("#1       0.10s best:208873 next:[208874,225336] main\n#Done    0.14s main"))
