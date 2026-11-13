from __future__ import annotations

from typing import Callable


def shrink(lifts: list[str], fits: Callable[[list[str]], bool]) -> list[str]:
    """A core of a refused set: still refused, and no lift can be dropped from it."""
    # TODO: write what the cut on a core says first, then shrink the list.
    return []


if __name__ == "__main__":
    print(shrink(["a", "b", "c"], lambda s: not {"a", "c"} <= set(s)))
