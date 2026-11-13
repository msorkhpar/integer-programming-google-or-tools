from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    region: str
    starts: tuple[int, ...]
    cost: tuple[int, ...]       # $k in its first, second, ... year of work
    value: int = 10


def start_variables(model: mathopt.Model, projects: list[Project]) -> dict:
    """Given: x[(pid, year)] for every allowed start year, and each project starts at most once."""
    x = {(p.pid, t): model.add_binary_variable(name=f"x_{p.pid}_{t}") for p in projects for t in p.starts}
    for p in projects:
        model.add_linear_constraint(sum(x[p.pid, t] for t in p.starts) <= 1, name=f"once_{p.pid}")
    return x


def spend(x: dict, projects: list[Project], year: int):
    """Given: what the projects spend in one year, as an expression (0 when nothing can be spent)."""
    return sum(p.cost[year - t] * x[p.pid, t] for p in projects for t in p.starts if 0 <= year - t < len(p.cost))


def add_cash_rules(model: mathopt.Model, x: dict, projects: list[Project], budgets: dict[int, int],
                   carry_share: float, floors: dict[str, int]) -> None:
    """Carry-over cash rows with a cap on what each year carries out, and a minimum spend per region."""
    years = sorted(budgets)
    carry = {y: model.add_variable(lb=0, name=f"carry_{y}") for y in years}
    for i, y in enumerate(years):
        incoming = carry[years[i - 1]] if i else 0
        model.add_linear_constraint(spend(x, projects, y) + carry[y] - incoming <= budgets[y], name=f"cash_{y}")
        model.add_linear_constraint(carry[y] <= carry_share * budgets[y], name=f"carry_cap_{y}")
    for region, floor in floors.items():
        members = [p for p in projects if p.region == region]
        total = mathopt.LinearExpression() + sum(spend(x, members, y) for y in years)
        model.add_linear_constraint(total >= floor, name=f"floor_{region}")


def build(projects: list[Project], budgets: dict[int, int], carry_share: float,
          floors: dict[str, int]) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="carry-over")
    x = start_variables(model, projects)
    add_cash_rules(model, x, projects, budgets, carry_share, floors)
    model.maximize(sum(p.value * x[p.pid, t] for p in projects for t in p.starts))
    return model, x


if __name__ == "__main__":
    model, x = build([Project("N1", "N", (2027, 2028), (60,))], {2027: 50, 2028: 50}, 0.5, {"N": 60})
    print(mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason.name)
