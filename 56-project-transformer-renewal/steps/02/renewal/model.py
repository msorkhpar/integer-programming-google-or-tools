"""The MathOpt model: when to replace each candidate transformer, within each year's budget."""

from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from .fleet import Transformer
from .request import Request
from .risk import risk_removed


@dataclass
class Built:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]      # x[i, t] = 1: replace transformer i in year t
    budget: dict[int, mathopt.LinearConstraint]     # one row per year


def candidates(fleet: list[Transformer], request: Request) -> list[Transformer]:
    return [t for t in fleet if t.age >= request.min_age]


def build(fleet: list[Transformer], request: Request) -> Built:
    model = mathopt.Model(name="renewal")
    units, years = candidates(fleet, request), request.plan_years()
    x = {(t.tid, y): model.add_binary_variable(name=f"x_{t.tid}_{y}") for t in units for y in years}
    for t in units:
        model.add_linear_constraint(sum(x[t.tid, y] for y in years) <= 1, name=f"once_{t.tid}")
    budget = {y: model.add_linear_constraint(sum(t.cost * x[t.tid, y] for t in units) <= request.budget,
                                             name=f"budget_{y}")
              for y in years}
    model.maximize(sum(risk_removed(t, y, request) * x[t.tid, y] for t in units for y in years))
    return Built(model, x, budget)
