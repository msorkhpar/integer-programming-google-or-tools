from __future__ import annotations

from typing import Callable


def deletion_filter(rules: list[str], feasible: Callable[[list[str]], bool]) -> list[str]:
    """One irreducible conflict among `rules`, in their input order, or [] if they can all hold.

    `feasible(subset)` answers whether the rules in `subset` can hold together (one solve each).
    Each rule is tested once, in order, and left out whenever the rules kept so far stay infeasible
    without it.
    """
    # TODO: test each rule once, in order, and keep only what the conflict needs.
    return list(rules)


if __name__ == "__main__":
    clash = lambda s: not {"a", "b"} <= set(s)
    print(deletion_filter(["a", "b", "c"], clash))
