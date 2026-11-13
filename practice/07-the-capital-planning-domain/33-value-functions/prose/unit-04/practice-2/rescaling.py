from __future__ import annotations

from typing import Callable

TIED = 1e-9   # values closer than this are a tie, listed by name


def ranking(values: dict[str, float]) -> list[str]:
    """Names from the highest value to the lowest; near-equal values count as tied, in name order."""
    # TODO
    return list(values)

def survives_rescaling(value: Callable[[dict, dict], float], benefits: dict[str, dict[str, float]],
                       reference: dict[str, float], factors: dict[str, float]) -> bool:
    """Whether `value` ranks the projects the same after every measure and its reference are restated."""
    # TODO: rank, restate every measure and its reference, rank again.
    return True


if __name__ == "__main__":
    def raw_sum(benefit, reference):
        return sum(benefit.values())

    projects = {"A": {"time": 10.0, "cost": 1.0}, "B": {"time": 1.0, "cost": 5.0}}
    print(survives_rescaling(raw_sum, projects, {"time": 10.0, "cost": 5.0}, {"time": 0.1, "cost": 1.0}))
