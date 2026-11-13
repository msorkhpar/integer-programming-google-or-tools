"""The one-period selection model of lesson 1.1.3, written for any GridCap portfolio.

`build` gives the LP relaxation (every x in [0, 1]) or the MILP. `solve_lp` solves the relaxation
with some variables held at 0 or 1: that is one node of a branch-and-bound tree.
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
    x: dict[str, mathopt.Variable]


def build(portfolio: Portfolio, integer: bool = False, yearly: bool = False) -> Selection:
    """Budget, must-do, parent and alternative-group rows over one x per project.

    With `yearly`, the one capital budget row becomes one row per year: every project starts in its
    earliest year, and its spend in each year must fit that year's budget.
    """
    model = mathopt.Model(name=f"{portfolio.name}-selection")
    x = {p.project_id: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}")
         for p in portfolio.projects}
    if yearly:
        for year in portfolio.years:
            model.add_linear_constraint(
                sum(p.spend(p.earliest_start).get(year, 0) * x[p.project_id] for p in portfolio.projects)
                <= portfolio.budget[year], name=f"budget_{year}")
    else:
        model.add_linear_constraint(sum(p.capex * x[p.project_id] for p in portfolio.projects)
                                    <= portfolio.capital_budget, name="budget")
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name=f"must_{p.project_id}")
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent], name=f"parent_{p.project_id}")
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for group, members in groups.items():
        model.add_linear_constraint(sum(x[i] for i in members) <= 1, name=f"alt_{group}")
    model.maximize(sum(p.value * x[p.project_id] for p in portfolio.projects))
    return Selection(model, x)


@dataclass(frozen=True)
class LP:
    status: str                # "optimal" or "infeasible"
    value: float | None        # the LP's objective value, None when infeasible
    x: dict[str, float]        # project id -> value in [0, 1]


def solve_lp(sel: Selection, fixed: dict[str, int]) -> LP:
    """The relaxation with each variable in `fixed` held at its 0 or 1; the others stay in [0, 1]."""
    for pid, var in sel.x.items():
        var.lower_bound = fixed.get(pid, 0)
        var.upper_bound = fixed.get(pid, 1)
    result = mathopt.solve(sel.model, mathopt.SolverType.GLOP)
    reason = result.termination.reason
    if reason == mathopt.TerminationReason.INFEASIBLE:
        return LP("infeasible", None, {})
    if reason != mathopt.TerminationReason.OPTIMAL:
        raise RuntimeError(f"GLOP stopped with {reason.name}")
    return LP("optimal", result.objective_value(), {pid: result.variable_values(v) for pid, v in sel.x.items()})


def solve_milp(sel: Selection) -> mathopt.SolveResult:
    """Solve the MILP with HiGHS, keeping its stray debug line out of the output (OR-Tools 9.15)."""
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(sel.model, mathopt.SolverType.HIGHS)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


def knapsack_model(items, budget: int, integer: bool = True) -> Selection:
    """The budget-only selection of lesson 3.2.4 over `knapsack.Item`s: one row, no other rule."""
    model = mathopt.Model(name="knapsack")
    x = {it.name: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{it.name}") for it in items}
    model.add_linear_constraint(sum(it.cost * x[it.name] for it in items) <= budget, name="budget")
    model.maximize(sum(it.value * x[it.name] for it in items))
    return Selection(model, x)
