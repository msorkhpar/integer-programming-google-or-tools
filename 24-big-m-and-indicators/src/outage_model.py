"""Ordering work that needs the same outage: a disjunction per pair, written as big-M or as the hull.

Each job j has a duration d[j] in months and a start month s[j] in [0, H - d[j]]. Two jobs that
share an outage cannot overlap: either i finishes before j starts, or j finishes before i starts.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from ortools.math_opt.python import mathopt


@dataclass
class OutageModel:
    model: mathopt.Model
    start: dict[str, mathopt.Variable]
    first: dict[tuple[str, str], mathopt.Variable]     # first[i, j] = 1: i goes before j


def build(durations: dict[str, int], horizon: int, form: str, *, integer: bool = True) -> OutageModel:
    model = mathopt.Model(name=f"outage {form}")
    start = {j: model.add_variable(lb=0, ub=horizon - d, name=f"s_{j}") for j, d in durations.items()}
    first = {}
    for i, j in combinations(durations, 2):
        y = model.add_variable(lb=0, ub=1, is_integer=integer, name=f"first_{i}_{j}")
        first[i, j] = y
        if form == "big_m":
            add_big_m(model, start, durations, horizon, i, j, y)
        elif form == "hull":
            add_hull(model, start, durations, horizon, i, j, y)
        else:
            raise ValueError(form)
    # Every month a job is unfinished its asset waits: minimize the sum of finish months.
    model.minimize(sum(start[j] + d for j, d in durations.items()))
    return OutageModel(model, start, first)


def add_big_m(model, start, d, horizon, i, j, y) -> None:
    """y = 1: i before j; y = 0: j before i. M = horizon: the most s_i + d_i - s_j can be."""
    big = horizon
    model.add_linear_constraint(start[i] + d[i] <= start[j] + big * (1 - y), name=f"{i}_before_{j}")
    model.add_linear_constraint(start[j] + d[j] <= start[i] + big * y, name=f"{j}_before_{i}")


def add_hull(model, start, d, horizon, i, j, y) -> None:
    """Each order gets its own copy of the two starts, scaled by that order's binary."""
    copies = {}
    for side, on in (("a", y), ("b", 1 - y)):
        for k in (i, j):
            copies[side, k] = model.add_variable(lb=0, name=f"s_{k}_{side}_{i}{j}")
            model.add_linear_constraint(copies[side, k] <= (horizon - d[k]) * on, name=f"cap_{k}_{side}_{i}{j}")
    for k in (i, j):
        model.add_linear_constraint(start[k] == copies["a", k] + copies["b", k], name=f"split_{k}_{i}{j}")
    model.add_linear_constraint(copies["a", i] + d[i] * y <= copies["a", j], name=f"{i}_before_{j}")
    model.add_linear_constraint(copies["b", j] + d[j] * (1 - y) <= copies["b", i], name=f"{j}_before_{i}")
