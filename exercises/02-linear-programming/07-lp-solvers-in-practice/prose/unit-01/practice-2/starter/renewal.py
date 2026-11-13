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
    # TODO: one variable per district with its bounds, the budget and crews rows, the objective,
    # then solve with `solver` and read the status before the value.
    return 0.0


def relative_gap(a: float, b: float) -> float:
    """|a - b| measured against the larger magnitude, and never against less than 1."""
    # TODO
    return 1.0


def all_agree(values: dict[str, float | None], tol: float = 1e-6) -> bool:
    """True when every solver returned a value and every pair is within `tol` relative gap."""
    # TODO: a missing value is a disagreement; otherwise compare every pair with relative_gap.
    return False


if __name__ == "__main__":
    demo = [District("North", 9, 4, 2, 10), District("South", 7, 3, 3, 8), District("East", 5, 2, 1, 12)]
    values = {s.name: solve_on(demo, 40, 30, s)
              for s in (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS, mathopt.SolverType.PDLP)}
    print(values, all_agree(values))
