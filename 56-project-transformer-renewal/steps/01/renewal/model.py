"""The MathOpt model: one yes-or-no decision per transformer, one budget row."""

from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from .fleet import Transformer, risk
from .request import Request


@dataclass
class Built:
    model: mathopt.Model
    x: dict[str, mathopt.Variable]          # x[i] = 1: replace transformer i this year
    budget: mathopt.LinearConstraint


def build(fleet: list[Transformer], request: Request) -> Built:
    model = mathopt.Model(name="renewal")
    x = {t.tid: model.add_binary_variable(name=f"x_{t.tid}") for t in fleet}
    budget = model.add_linear_constraint(
        sum(t.cost * x[t.tid] for t in fleet) <= request.budget, name="budget")
    model.maximize(sum(risk(t) * x[t.tid] for t in fleet))
    return Built(model, x, budget)
