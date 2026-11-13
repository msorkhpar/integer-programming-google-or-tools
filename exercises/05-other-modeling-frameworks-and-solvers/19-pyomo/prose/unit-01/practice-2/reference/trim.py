from __future__ import annotations

from dataclasses import dataclass

import pyomo.environ as pyo


@dataclass(frozen=True)
class Circuit:
    hours: int                  # crew hours to trim it
    risk: float                 # risk removed if it is trimmed
    months: tuple[str, ...]     # the months it may be trimmed in


def trim_plan(circuits: dict[str, Circuit], crew_hours: dict[str, int]) -> tuple[float, dict[str, str]]:
    """The most risk the crews can remove, and the month each trimmed circuit is trimmed in."""
    m = pyo.ConcreteModel()
    m.C = pyo.Set(initialize=list(circuits))
    m.M = pyo.Set(initialize=list(crew_hours))
    m.A = pyo.Set(dimen=2, initialize=[(c, k) for c, circuit in circuits.items() for k in circuit.months
                                       if k in crew_hours])     # a month with no crew hours is no option
    m.hours = pyo.Param(m.C, initialize={c: circuit.hours for c, circuit in circuits.items()})
    m.risk = pyo.Param(m.C, initialize={c: circuit.risk for c, circuit in circuits.items()})
    m.cap = pyo.Param(m.M, initialize=crew_hours)
    m.x = pyo.Var(m.A, domain=pyo.Binary)

    def once_rule(m, c):
        terms = [m.x[c, k] for (d, k) in m.A if d == c]
        if not terms:
            return pyo.Constraint.Skip
        return sum(terms) <= 1
    m.once = pyo.Constraint(m.C, rule=once_rule)

    def crews_rule(m, k):
        terms = [m.hours[c] * m.x[c, j] for (c, j) in m.A if j == k]
        if not terms:
            return pyo.Constraint.Skip
        return sum(terms) <= m.cap[k]
    m.crews = pyo.Constraint(m.M, rule=crews_rule)

    m.removed = pyo.Objective(expr=sum(m.risk[c] * m.x[c, k] for (c, k) in m.A), sense=pyo.maximize)
    solver = pyo.SolverFactory("appsi_highs")
    solver.config.mip_gap = 0.0
    solver.solve(m)
    plan = {c: k for (c, k) in m.A if pyo.value(m.x[c, k]) > 0.5}
    return pyo.value(m.removed), plan


if __name__ == "__main__":
    lines = {"L1": Circuit(60, 9.0, ("Apr", "May")), "L2": Circuit(50, 7.0, ("Apr",)),
             "L3": Circuit(40, 4.0, ("May", "Jun"))}
    print(trim_plan(lines, {"Apr": 80, "May": 60, "Jun": 30}))
