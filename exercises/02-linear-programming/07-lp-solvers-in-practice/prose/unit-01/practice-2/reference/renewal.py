from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class District:
    name: str
    value_per_km: float      # benefit of one km renewed, $k
    cost_per_km: float       # $k
    hours_per_km: float      # crew hours
    max_km: float
    min_km: float = 0.0      # km a regulator has ordered


def solve_on(districts: list[District], budget: float, hours: float, solver: mathopt.SolverType) -> float | None:
    """Build the renewal LP, solve it with `solver`, and return its objective, or None if not OPTIMAL."""
    model = mathopt.Model(name="renewal")
    km = {d.name: model.add_variable(lb=d.min_km, ub=d.max_km, name=f"km_{d.name}") for d in districts}
    model.add_linear_constraint(sum(d.cost_per_km * km[d.name] for d in districts) <= budget, name="budget")
    model.add_linear_constraint(sum(d.hours_per_km * km[d.name] for d in districts) <= hours, name="crews")
    model.maximize(sum(d.value_per_km * km[d.name] for d in districts))
    result = mathopt.solve(model, solver)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None
    return result.objective_value()


def relative_gap(a: float, b: float) -> float:
    """|a - b| measured against the larger magnitude, and never against less than 1."""
    return abs(a - b) / max(1.0, abs(a), abs(b))


def all_agree(values: dict[str, float | None], tol: float = 1e-6) -> bool:
    """True when every solver returned a value and every pair is within `tol` relative gap."""
    if any(v is None for v in values.values()):
        return False
    found = list(values.values())
    return all(relative_gap(a, b) <= tol for i, a in enumerate(found) for b in found[i + 1:])


if __name__ == "__main__":
    demo = [District("North", 9, 4, 2, 10), District("South", 7, 3, 3, 8), District("East", 5, 2, 1, 12)]
    values = {s.name: solve_on(demo, 40, 30, s)
              for s in (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS, mathopt.SolverType.PDLP)}
    print(values, all_agree(values))
