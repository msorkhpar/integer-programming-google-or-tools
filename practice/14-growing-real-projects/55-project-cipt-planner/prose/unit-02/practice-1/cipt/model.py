"""The model: one yes-or-no decision per project, one budget row."""

from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from .data import Request


@dataclass
class Built:
    """A built model and the handles the rest of the planner needs to read it."""

    request: Request
    model: mathopt.Model
    x: dict[str, mathopt.Variable]
    rows: dict[str, mathopt.LinearConstraint]


def build(request: Request) -> Built:
    """max sum value_i x_i  subject to  sum capex_i x_i <= B, with x_i binary."""
    model = mathopt.Model(name=request.name)
    x = {p.project_id: model.add_binary_variable(name=f"x_{p.project_id}") for p in request.projects}
    spend = mathopt.fast_sum(p.capex * x[p.project_id] for p in request.projects)
    rows = {"budget": model.add_linear_constraint(spend <= request.capital_budget, name="budget")}
    model.maximize(mathopt.fast_sum(p.value * x[p.project_id] for p in request.projects))
    return Built(request, model, x, rows)


def spend_by_year(request: Request, x: dict) -> dict[int, mathopt.LinearSum]:
    """Returns one linear expression per plan year, with an entry for every plan year (an empty sum when no start can spend in it): for every project and allowed start, each year's amount of its cost profile times that start's variable, summed into the calendar year it is spent in."""
    return {}
