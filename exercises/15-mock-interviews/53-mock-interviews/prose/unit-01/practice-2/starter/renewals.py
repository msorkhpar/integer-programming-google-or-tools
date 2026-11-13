from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Renewal:
    rid: str
    starts: tuple[int, ...]            # the years it may start in
    cost: tuple[int, ...]              # $k spent in its first, second, ... year of work
    value: int = 10
    parent: str | None = None          # may start only `lag` years after this renewal starts
    lag: int = 0                       # start to start, in years
    group: str | None = None           # alternatives for one main share a group


def start_variables(model: mathopt.Model, renewals: list[Renewal]) -> dict:
    """x[(rid, year)] = 1 when the renewal starts in that year; only years in its window exist."""
    return {(r.rid, t): model.add_binary_variable(name=f"x_{r.rid}_{t}") for r in renewals for t in r.starts}


def add_once_rows(model: mathopt.Model, x: dict, renewals: list[Renewal]) -> None:
    """Given: each renewal starts at most once."""
    for r in renewals:
        model.add_linear_constraint(sum(x[r.rid, t] for t in r.starts) <= 1, name=f"once_{r.rid}")


def add_rules(model: mathopt.Model, x: dict, renewals: list[Renewal], budgets: dict[int, int]) -> None:
    """The budget of every year, every predecessor with its lag, and every alternative group."""
    # TODO: write the formulation's rows here.
    return None


def build(renewals: list[Renewal], budgets: dict[int, int]) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="pipe-renewals")
    x = start_variables(model, renewals)
    add_once_rows(model, x, renewals)
    add_rules(model, x, renewals, budgets)
    model.maximize(sum(r.value * x[r.rid, t] for r in renewals for t in r.starts))
    return model, x


if __name__ == "__main__":
    mains = [Renewal("R1", (2027, 2028), (40, 40)), Renewal("R2", (2028,), (30,), parent="R1", lag=1)]
    model, x = build(mains, {2027: 50, 2028: 50})
    print(len(list(model.linear_constraints())), "rows")
