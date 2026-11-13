"""The CP-SAT model: one yes-or-no start variable per project and year, and one row family per rule."""

from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model

from .portfolio import Project
from .request import Request


@dataclass
class Built:
    model: cp_model.CpModel
    x: dict[tuple[str, int], cp_model.IntVar]      # x[pid, year] = 1: the project starts that year


def window(project: Project, request: Request) -> list[int]:
    """The plan years in which the project may start."""
    return [y for y in request.plan_years() if project.earliest <= y <= project.latest]


def spend(projects: list[Project], x: dict, year: int):
    """What the plan spends in a year: each project's whole cost, in the year it starts."""
    return sum(p.cost * x[p.pid, year] for p in projects if (p.pid, year) in x)


def build(projects: list[Project], request: Request) -> Built:
    model = cp_model.CpModel()
    x = {(p.pid, y): model.new_bool_var(f"x_{p.pid}_{y}") for p in projects for y in window(p, request)}
    for p in projects:
        model.add(sum(x[p.pid, y] for y in window(p, request)) <= 1).with_name(f"once_{p.pid}")
    for y in request.plan_years():
        model.add(spend(projects, x, y) <= request.budget).with_name(f"budget_{y}")
        if request.max_starts is not None:
            starts = sum(var for (_, year), var in x.items() if year == y)
            model.add(starts <= request.max_starts).with_name(f"starts_{y}")
    model.maximize(sum(p.value * x[p.pid, y] for p in projects for y in window(p, request)))
    return Built(model, x)
