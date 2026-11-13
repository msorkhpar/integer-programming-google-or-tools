from __future__ import annotations

from typing import Callable


def shrink(lifts: list[str], fits: Callable[[list[str]], bool]) -> list[str]:
    """A core of a refused set: still refused, and no lift can be dropped from it."""
    core = list(lifts)
    for lift in lifts:
        rest = [k for k in core if k != lift]
        if not fits(rest):
            core = rest
    return core


if __name__ == "__main__":
    print(shrink(["a", "b", "c"], lambda s: not {"a", "c"} <= set(s)))
