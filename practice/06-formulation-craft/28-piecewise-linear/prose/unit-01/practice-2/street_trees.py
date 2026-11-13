from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Street:
    name: str
    xs: tuple[float, ...]       # trees at each breakpoint, increasing, starting at 0
    ys: tuple[float, ...]       # benefit at each breakpoint


def add_benefit(model: mathopt.Model, trees: mathopt.Variable, xs: tuple[float, ...],
                ys: tuple[float, ...]):
    """Rows for one street; returns an expression equal to its benefit at `trees`."""
    # TODO: the street's benefit as a function of its trees, and no more trees than the curve covers.
    return 0 * trees


def build(streets: list[Street], stock: float) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="street trees")
    trees = {s.name: model.add_variable(lb=0, name=f"trees_{s.name}") for s in streets}
    model.add_linear_constraint(sum(trees.values()) <= stock, name="stock")
    model.maximize(sum(add_benefit(model, trees[s.name], s.xs, s.ys) for s in streets))
    return model, trees


if __name__ == "__main__":
    elm = Street("Elm St", (0, 10, 25, 40), (0, 30, 51, 57))
    model, trees = build([elm], 20)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    print(result.objective_value())
