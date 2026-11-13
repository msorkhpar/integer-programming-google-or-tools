from __future__ import annotations

import itertools
from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Talk:
    name: str
    speaker: str
    lab_hours: int             # hours of the shared lab the talk's demonstration needs
    value: int


def clashes(talks: list[Talk], lab_hours: int) -> set[frozenset[str]]:
    """Pairs of talks no programme can accept together."""
    pairs = set()
    for a, b in itertools.combinations(talks, 2):
        same_speaker = a.speaker == b.speaker                         # a speaker gives one talk
        too_long = a.lab_hours + b.lab_hours > lab_hours              # the two overrun the lab
        if same_speaker or too_long:
            pairs.add(frozenset((a.name, b.name)))
    return pairs


def add_clash_rows(model: mathopt.Model, x: dict, pairs: set[frozenset[str]]) -> int:
    """Cover every clash with a row 'at most one of these talks', as few and as wide as greedily found."""
    names = sorted(x)
    clash = {n: {m for m in names if frozenset((n, m)) in pairs} for n in names}
    covered: set[frozenset[str]] = set()
    rows = 0
    for first in names:
        for second in sorted(clash[first]):
            if frozenset((first, second)) in covered:
                continue
            group = [first, second]
            for other in names:
                if other not in group and all(other in clash[g] for g in group):
                    group.append(other)
            model.add_linear_constraint(sum(x[g] for g in group) <= 1, name=f"clash_{rows}")
            covered |= {frozenset(p) for p in itertools.combinations(group, 2)}
            rows += 1
    return rows


def build(talks: list[Talk], lab_hours: int, *, integer: bool = True) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="programme")
    x = {t.name: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{t.name}") for t in talks}
    add_clash_rows(model, x, clashes(talks, lab_hours))
    model.maximize(sum(t.value * x[t.name] for t in talks))
    return model, x


if __name__ == "__main__":
    talks = [Talk("T1", "ana", 5, 3), Talk("T2", "ben", 4, 2), Talk("T3", "ana", 1, 1)]
    print(sorted(sorted(p) for p in clashes(talks, 8)))
