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
    """A new module. Returns a Built, a dataclass holding the MathOpt model, the variables `x` keyed by transformer id, and the budget row: one binary variable per transformer named `x_<tid>`, one row named `budget` keeping the summed cost of the replaced units within request.budget, and the summed risk of the replaced units as the objective to maximize."""
    return None
