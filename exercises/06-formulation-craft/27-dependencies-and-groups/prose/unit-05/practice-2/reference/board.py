from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    kind: str          # "maintenance" or "growth"
    cost: int


def add_spend_rules(model: mathopt.Model, x: dict, projects: list[Project], budget: int, use: float,
                    low: float, high: float) -> None:
    """Spend between use x budget and budget; maintenance between low and high of the plan's spend."""
    total = sum(p.cost * x[p.pid] for p in projects)
    upkeep = sum(p.cost * x[p.pid] for p in projects if p.kind == "maintenance")
    model.add_linear_constraint(total <= budget, name="budget")
    model.add_linear_constraint(total >= use * budget, name="use_it")
    model.add_linear_constraint(upkeep >= low * total, name="upkeep_low")
    model.add_linear_constraint(upkeep <= high * total, name="upkeep_high")


def build(projects: list[Project], budget: int, use: float, low: float,
          high: float) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="water-board")
    x = {p.pid: model.add_binary_variable(name=f"x_{p.pid}") for p in projects}
    add_spend_rules(model, x, projects, budget, use, low, high)
    return model, x


if __name__ == "__main__":
    projects = [Project("PIPE", "maintenance", 300), Project("TANK", "growth", 500)]
    model, x = build(projects, 900, 0.8, 0.3, 0.5)
    print(model.get_num_linear_constraints(), "rows")
