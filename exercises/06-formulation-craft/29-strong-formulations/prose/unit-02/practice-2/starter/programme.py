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
    # TODO: the pairs that clash, and why.
    return set()


def add_clash_rows(model: mathopt.Model, x: dict, pairs: set[frozenset[str]]) -> int:
    """Cover every clash with a row 'at most one of these talks', as few and as wide as greedily found."""
    # TODO: rows that cover every clash.
    return 0


def build(talks: list[Talk], lab_hours: int, *, integer: bool = True) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="programme")
    x = {t.name: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{t.name}") for t in talks}
    add_clash_rows(model, x, clashes(talks, lab_hours))
    model.maximize(sum(t.value * x[t.name] for t in talks))
    return model, x


if __name__ == "__main__":
    talks = [Talk("T1", "ana", 5, 3), Talk("T2", "ben", 4, 2), Talk("T3", "ana", 1, 1)]
    print(sorted(sorted(p) for p in clashes(talks, 8)))
