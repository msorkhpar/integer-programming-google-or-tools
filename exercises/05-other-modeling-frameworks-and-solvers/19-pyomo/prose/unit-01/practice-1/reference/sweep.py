from __future__ import annotations

import pyomo.environ as pyo


def build(projects: dict[str, tuple[float, float]], budget: float) -> pyo.ConcreteModel:
    """Fund projects (name -> (cost, value)) within `budget`, maximizing value. The budget is a mutable Param."""
    m = pyo.ConcreteModel()
    m.P = pyo.Set(initialize=list(projects))
    m.cost = pyo.Param(m.P, initialize={p: c for p, (c, v) in projects.items()})
    m.value = pyo.Param(m.P, initialize={p: v for p, (c, v) in projects.items()})
    m.budget = pyo.Param(initialize=budget, mutable=True)
    m.x = pyo.Var(m.P, domain=pyo.Binary)
    m.spend = pyo.Constraint(expr=sum(m.cost[p] * m.x[p] for p in m.P) <= m.budget)
    m.total = pyo.Objective(expr=sum(m.value[p] * m.x[p] for p in m.P), sense=pyo.maximize)
    return m


def sweep(projects: dict[str, tuple[float, float]], budgets: list[float]) -> list[float]:
    """The best total value at each budget, from one model built once and re-solved."""
    solver = pyo.SolverFactory("appsi_highs")
    solver.config.mip_gap = 0.0
    m = build(projects, budgets[0])
    values = []
    for b in budgets:
        m.budget = b
        solver.solve(m)
        values.append(pyo.value(m.total))
    return values


if __name__ == "__main__":
    print(sweep({"A": (4, 7), "B": (3, 5), "C": (2, 3)}, [3, 5, 9]))
