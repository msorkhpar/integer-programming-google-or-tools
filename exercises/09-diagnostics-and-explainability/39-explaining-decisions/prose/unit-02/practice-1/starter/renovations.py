from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Renovation:
    name: str
    cost: int           # $k
    value: int          # $k of benefit
    mandatory: bool = False


def build(items: list[Renovation], budget: int) -> tuple[mathopt.Model, dict[str, mathopt.Variable]]:
    """The library board's model: pick renovations within the budget; mandatory ones always."""
    model = mathopt.Model(name="renovations")
    x = {r.name: model.add_binary_variable(name=f"x_{r.name}") for r in items}
    model.add_linear_constraint(sum(r.cost * x[r.name] for r in items) <= budget, name="budget")
    for r in items:
        if r.mandatory:
            model.add_linear_constraint(x[r.name] == 1, name=f"must_{r.name}")
    model.maximize(sum(r.value * x[r.name] for r in items))
    return model, x


def best(model: mathopt.Model, x: dict[str, mathopt.Variable]) -> tuple[float, set[str]] | None:
    """(best value, chosen names), or None when the model has no feasible plan."""
    result = mathopt.solve(model, mathopt.SolverType.HIGHS,
                           params=mathopt.SolveParameters(relative_gap_tolerance=0.0))   # a proven optimum
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None
    return result.objective_value(), {name for name, v in x.items() if result.variable_values(v) > 0.5}


def forcing_cost(items: list[Renovation], budget: int, name: str) -> dict:
    """Reverse the best plan's decision on `name`, re-solve, and say what it costs and what changes."""
    # TODO: solve the board's model, write the forcing as a named row, re-solve, compare.
    return {"action": "in", "cost": 0, "dropped": [], "added": []}

if __name__ == "__main__":
    items = [Renovation("roof", 40, 60), Renovation("lift", 30, 20, mandatory=True)]
    print(forcing_cost(items, 60, "roof"))
