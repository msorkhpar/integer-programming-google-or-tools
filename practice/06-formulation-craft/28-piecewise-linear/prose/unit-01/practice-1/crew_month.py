from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Job:
    jid: str
    hours: float


def add_labor_rules(model: mathopt.Model, x: dict, jobs: list[Job], tiers: list[tuple[float, float]],
                    budget: float) -> None:
    """The month's tiered labor cost within the budget, and no more hours than the last tier allows."""
    # TODO: the month's hours, a variable per tier, the hours row and the budget row.
    return None


def build(jobs: list[Job], tiers: list[tuple[float, float]], budget: float) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="crew month")
    x = {j.jid: model.add_binary_variable(name=f"x_{j.jid}") for j in jobs}
    add_labor_rules(model, x, jobs, tiers, budget)
    model.maximize(sum(j.hours * x[j.jid] for j in jobs))
    return model, x


if __name__ == "__main__":
    jobs = [Job("Elm St", 100), Job("Oak Ave", 80), Job("Pine Rd", 40)]
    model, x = build(jobs, [(160, 60.0), (200, 90.0), (240, 120.0)], 12_000)
    print(model.get_num_linear_constraints(), "rows")
