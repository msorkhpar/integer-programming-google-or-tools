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
    carry: dict[int, cp_model.IntVar]               # carry[year]: $k carried from that year into the next


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
        starts = sum(x[p.pid, y] for y in window(p, request))
        if p.pid in request.must_do:
            model.add(starts == 1).with_name(f"must_{p.pid}")      # started in exactly one year
        else:
            model.add(starts <= 1).with_name(f"once_{p.pid}")
    years = request.plan_years()
    cap = request.budget * request.carry // 100
    carry = {y: model.new_int_var(0, cap, f"carry_{y}") for y in years[:-1]}   # 0: nothing is borrowed
    for y in years:
        # The year's spend, plus what it passes on, within its budget plus what it was passed.
        model.add(spend(projects, x, y) + carry.get(y, 0) <= request.budget + carry.get(y - 1, 0)
                  ).with_name(f"budget_{y}")
        if request.max_starts is not None:
            starts = sum(var for (_, year), var in x.items() if year == y)
            model.add(starts <= request.max_starts).with_name(f"starts_{y}")
    for region, pct in request.shares.items():
        if pct == 0:
            continue                             # a share of 0 sets no minimum
        members = [p for p in projects if p.region == region]
        for y in request.plan_years():
            # 100 * (the region's spend) >= pct * (the year's spend): the share as a linear row.
            model.add(100 * spend(members, x, y) >= pct * spend(projects, x, y)).with_name(f"share_{region}_{y}")
    model.maximize(sum(p.value * x[p.pid, y] for p in projects for y in window(p, request)))
    return Built(model, x, carry)
