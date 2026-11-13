from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Project:
    pid: str
    units: int       # transformers the project needs
    cost: int        # $k, without the transformers' delivery


def add_order_rules(model: mathopt.Model, x: dict, projects: list[Project], min_order: int,
                    max_order: int, delivery_fee: int, budget: int) -> None:
    """No order, or one between min_order and max_order units with a delivery fee; all within budget."""
    # TODO: the order switch, its two rows, and the budget row.
    return None


def build(projects: list[Project], min_order: int, max_order: int, delivery_fee: int,
          budget: int) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="transformer-order")
    x = {p.pid: model.add_binary_variable(name=f"x_{p.pid}") for p in projects}
    add_order_rules(model, x, projects, min_order, max_order, delivery_fee, budget)
    model.maximize(sum(x.values()))
    return model, x


if __name__ == "__main__":
    projects = [Project("F1", 6, 50), Project("F2", 5, 40), Project("F3", 0, 25)]
    model, x = build(projects, 10, 30, 20, 200)
    print(len(list(model.linear_constraints())), "rows")
