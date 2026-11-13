from __future__ import annotations

from typing import Callable

TIED = 1e-9   # values closer than this are a tie, listed by name


def ranking(values: dict[str, float]) -> list[str]:
    """Names from the highest value to the lowest; near-equal values count as tied, in name order."""
    order = sorted(values, key=lambda name: (-values[name], name))
    tied_groups, group = [], [order[0]] if order else []
    for name in order[1:]:
        if values[group[-1]] - values[name] <= TIED:
            group.append(name)
        else:
            tied_groups.append(sorted(group))
            group = [name]
    if group:
        tied_groups.append(sorted(group))
    return [name for g in tied_groups for name in g]


def survives_rescaling(value: Callable[[dict, dict], float], benefits: dict[str, dict[str, float]],
                       reference: dict[str, float], factors: dict[str, float]) -> bool:
    """Whether `value` ranks the projects the same after every measure and its reference are restated."""
    before = ranking({p: value(b, reference) for p, b in benefits.items()})
    restated_reference = {m: r * factors[m] for m, r in reference.items()}
    after = ranking({p: value({m: a * factors[m] for m, a in b.items()}, restated_reference)
                     for p, b in benefits.items()})
    return before == after


if __name__ == "__main__":
    def raw_sum(benefit, reference):
        return sum(benefit.values())

    projects = {"A": {"time": 10.0, "cost": 1.0}, "B": {"time": 1.0, "cost": 5.0}}
    print(survives_rescaling(raw_sum, projects, {"time": 10.0, "cost": 5.0}, {"time": 0.1, "cost": 1.0}))
