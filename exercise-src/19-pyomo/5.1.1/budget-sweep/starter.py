from __future__ import annotations

import pyomo.environ as pyo


def build(projects: dict[str, tuple[float, float]], budget: float) -> pyo.ConcreteModel:
    """Fund projects (name -> (cost, value)) within `budget`, maximizing value. The budget is a mutable Param."""
    m = pyo.ConcreteModel()
    # TODO: the set of projects, cost and value Params, a mutable budget Param, x, the spend row
    #       and the objective, named m.total.
    return m


def sweep(projects: dict[str, tuple[float, float]], budgets: list[float]) -> list[float]:
    """The best total value at each budget, from one model built once and re-solved."""
    # TODO: build once, then for each budget change m.budget, solve with appsi_highs and read m.total.
    return [0.0 for _ in budgets]


if __name__ == "__main__":
    print(sweep({"A": (4, 7), "B": (3, 5), "C": (2, 3)}, [3, 5, 9]))
