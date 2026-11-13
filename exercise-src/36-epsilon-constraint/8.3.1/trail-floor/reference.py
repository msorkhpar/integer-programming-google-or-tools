from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Trail:
    name: str
    visitors: int     # people per year
    acres: int        # habitat protected
    cost: int         # $k


def most_visitors(trails: list[Trail], budget: int, habitat_floor: int) -> tuple[str, ...] | None:
    """The trails to fund for the most visitors, protecting at least `habitat_floor` acres."""
    model = mathopt.Model(name="trails")
    fund = {t.name: model.add_binary_variable(name=f"fund_{t.name}") for t in trails}
    model.add_linear_constraint(sum(t.cost * fund[t.name] for t in trails) <= budget, name="budget")
    model.add_linear_constraint(sum(t.acres * fund[t.name] for t in trails) >= habitat_floor, name="pledge")
    model.maximize(sum(t.visitors * fund[t.name] for t in trails))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None
    values = result.variable_values()
    return tuple(sorted(name for name, var in fund.items() if values[var] > 0.5))


if __name__ == "__main__":
    park = [Trail("Ridge Loop", 900, 10, 40), Trail("Marsh Boardwalk", 400, 60, 35), Trail("Canyon Spur", 700, 25, 30)]
    print(most_visitors(park, 70, 50))
