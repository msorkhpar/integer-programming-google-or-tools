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
    """Stub: lesson 14.2.1 writes the model. Until then, an empty one."""
    return Built(request, mathopt.Model(name=request.name), {}, {})
