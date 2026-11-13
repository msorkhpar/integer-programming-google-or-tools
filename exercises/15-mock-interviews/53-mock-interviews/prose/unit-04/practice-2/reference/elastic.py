from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    year: int
    cost: int            # $k, all spent in its year
    must_do: bool = False


def select_variables(model: mathopt.Model, projects: list[Project]) -> dict[str, mathopt.Variable]:
    """Given: x[pid] = 1 when the project is funded, and every must-do funded."""
    x = {p.pid: model.add_binary_variable(name=f"x_{p.pid}") for p in projects}
    for p in projects:
        if p.must_do:
            model.add_linear_constraint(x[p.pid] == 1, name=f"must_{p.pid}")
    return x


def add_elastic_budgets(model: mathopt.Model, x: dict, projects: list[Project],
                        budgets: dict[int, int], penalty: dict[int, float]) -> None:
    """Each year's budget may be overspent, at penalty[year] per $k; minimize the total penalty."""
    over = {y: model.add_variable(lb=0, name=f"over_{y}") for y in budgets}
    for y, cap in budgets.items():
        spend = sum(p.cost * x[p.pid] for p in projects if p.year == y)
        model.add_linear_constraint(spend - over[y] <= cap, name=f"budget_{y}")
    model.minimize(sum(penalty[y] * over[y] for y in budgets))


def build(projects: list[Project], budgets: dict[int, int], penalty: dict[int, float]) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="elastic-budgets")
    x = select_variables(model, projects)
    add_elastic_budgets(model, x, projects, budgets, penalty)
    return model, x


if __name__ == "__main__":
    model, x = build([Project("M1", 2027, 80, True)], {2027: 50}, {2027: 1.0})
    print(mathopt.solve(model, mathopt.SolverType.HIGHS).objective_value())
