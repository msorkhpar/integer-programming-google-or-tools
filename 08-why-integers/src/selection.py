"""The one-period GridCap selection model of section 3, as a MILP or as its LP relaxation.

GridCap is a fictional utility's portfolio. This module builds the model of lesson 1.1.1 (one
capital budget, must-do, parent and alternative rules) and the helpers module 08's programs share.
"""

from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from gridcap import Portfolio


@dataclass
class Selection:
    model: mathopt.Model
    x: dict[str, mathopt.Variable]          # x[i] = 1: project i is funded


def groups_of(portfolio: Portfolio) -> dict[str, list[str]]:
    """Alternative group -> the projects in it."""
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    return groups


def build(portfolio: Portfolio, *, integer: bool = True, parent_form: str = "tight") -> Selection:
    """The selection model. integer=False gives its LP relaxation: the same rows, x between 0 and 1.

    parent_form "tight" writes the parent rule as x_c <= x_p; "loose" as x_c <= 2 x_p, which allows
    the same 0/1 plans but more fractional points (lesson 3.1.2).
    """
    model = mathopt.Model(name=f"{portfolio.name} selection")
    x = {p.project_id: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}")
         for p in portfolio.projects}
    model.add_linear_constraint(sum(p.capex * x[p.project_id] for p in portfolio.projects)
                                <= portfolio.capital_budget, name="budget")
    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name=f"must_{p.project_id}")
        if p.parent:
            room = 1 if parent_form == "tight" else 2
            model.add_linear_constraint(x[p.project_id] <= room * x[p.parent], name=f"parent_{p.project_id}")
    for g, members in groups_of(portfolio).items():
        model.add_linear_constraint(sum(x[i] for i in members) <= 1, name=f"alt_{g}")
    model.maximize(sum(p.value * x[p.project_id] for p in portfolio.projects))
    return Selection(model, x)


def solve_highs(model: mathopt.Model, params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
    """Solve with HiGHS, keeping the engine's stray debug line out of the program's output.

    The HiGHS bundled in OR-Tools 9.15.6755 prints a debug line on some MIP solves with no log
    requested, as C output buffered until exit. Standard output points at /dev/null for the solve, and the C
    buffer is flushed before it is restored.
    """
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


def lp_values(portfolio: Portfolio) -> tuple[float, dict[str, float]]:
    """The LP relaxation's value and each x_i, solved with GLOP."""
    lp = build(portfolio, integer=False)
    result = mathopt.solve(lp.model, mathopt.SolverType.GLOP)
    return result.objective_value(), {pid: result.variable_values(v) for pid, v in lp.x.items()}


def best_plan(portfolio: Portfolio) -> tuple[float, set[str]]:
    """The MILP's optimal value and plan, solved with HiGHS."""
    milp = build(portfolio)
    result = solve_highs(milp.model)
    return result.objective_value(), {pid for pid, v in milp.x.items() if result.variable_values(v) > 0.5}


def cost(portfolio: Portfolio, plan: set[str]) -> int:
    return sum(portfolio.project(i).capex for i in plan)


def value(portfolio: Portfolio, plan: set[str]) -> int:
    return sum(portfolio.project(i).value for i in plan)


def broken_rows(portfolio: Portfolio, plan: set[str]) -> list[str]:
    """The labels of the model's rows a 0/1 plan breaks, in the model's order."""
    broken = []
    if cost(portfolio, plan) > portfolio.capital_budget:
        broken.append("budget")
    for p in portfolio.projects:
        if p.must_do and p.project_id not in plan:
            broken.append(f"must_{p.project_id}")
        if p.parent and p.project_id in plan and p.parent not in plan:
            broken.append(f"parent_{p.project_id}")
    for g, members in groups_of(portfolio).items():
        if sum(i in plan for i in members) > 1:
            broken.append(f"alt_{g}")
    return broken
