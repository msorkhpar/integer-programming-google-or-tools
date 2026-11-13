from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Upgrade:
    name: str
    hours: int        # opening hours added per week
    seats: int        # reading-room seats added
    cost: int         # $k


def solved(model: mathopt.Model) -> mathopt.SolveResult | None:
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    return result if result.termination.reason == mathopt.TerminationReason.OPTIMAL else None


def frontier(upgrades: list[Upgrade], budget: int) -> list[tuple[int, int]]:
    """Every Pareto-optimal (hours, seats) score of the affordable choices, sorted by hours."""
    model = mathopt.Model(name="libraries")
    pick = [model.add_binary_variable(name=f"do_{u.name}") for u in upgrades]
    model.add_linear_constraint(sum(u.cost * v for u, v in zip(upgrades, pick)) <= budget, name="budget")
    hours = mathopt.LinearExpression() + sum(u.hours * v for u, v in zip(upgrades, pick))
    seats = mathopt.LinearExpression() + sum(u.seats * v for u, v in zip(upgrades, pick))
    points: list[tuple[int, int]] = []
    # TODO: generate every Pareto-optimal (hours, seats) score.
    return sorted(points)


if __name__ == "__main__":
    plans = [Upgrade("Eastside", 12, 20, 40), Upgrade("Harbor", 20, 5, 35), Upgrade("Old Town", 6, 30, 30)]
    print(frontier(plans, 70))
