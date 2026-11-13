from __future__ import annotations

from typing import Callable


def deletion_filter(rules: list[str], feasible: Callable[[set[str]], bool]) -> list[str]:
    """An irreducible infeasible subset of `rules`, or [] if they can all hold."""
    # TODO: check the whole set, then drop each rule in turn and put it back if the rest became feasible.
    return list(rules)


if __name__ == "__main__":
    caps = {"min_load": (5, None), "max_load": (None, 3), "truck": (None, 10)}

    def feasible(subset):
        low = max([caps[r][0] for r in subset if caps[r][0] is not None], default=0)
        high = min([caps[r][1] for r in subset if caps[r][1] is not None], default=float("inf"))
        return low <= high

    print(deletion_filter(list(caps), feasible))
