from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Pipe:
    pid: str
    km: float
    cost: int        # $k, the inspection's own cost


def add_inspection_rules(model: mathopt.Model, x: dict, pipes: list[Pipe], km_per_week: float,
                         weekly_rate: int, max_weeks: int, budget: int) -> None:
    """Whole weeks of rental cover the kilometres inspected; costs plus rental stay within the budget."""
    # TODO: the rental variable, the coverage row and the budget row.
    return None


def build(pipes: list[Pipe], km_per_week: float, weekly_rate: int, max_weeks: int,
          budget: int) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="pipe-inspection")
    x = {p.pid: model.add_binary_variable(name=f"x_{p.pid}") for p in pipes}
    add_inspection_rules(model, x, pipes, km_per_week, weekly_rate, max_weeks, budget)
    model.maximize(sum(p.km * x[p.pid] for p in pipes))
    return model, x


if __name__ == "__main__":
    mains = [Pipe("M1", 12.0, 40), Pipe("M2", 25.0, 90)]
    model, x = build(mains, 30.0, 50, 2, 300)
    print(len(list(model.linear_constraints())), "rows")
