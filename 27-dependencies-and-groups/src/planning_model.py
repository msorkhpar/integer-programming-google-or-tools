"""The multi-period GridCap planning model that every lesson of module 27 adds its rules to.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.

The model is the one of module 26: one binary x[i, t] per project and allowed start year, each
project's cost spread over the years it is worked on, a budget row per year and NPV to maximize.
`build` writes the dependency and group rules of this module as switches, so a lesson can turn one
off and show what it was doing.
"""

from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from gridcap import Portfolio, Project

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


@dataclass
class Plan:
    portfolio: Portfolio
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]          # x[i, t] = 1: project i starts in year t
    spend: dict[int, mathopt.LinearExpression] = field(default_factory=dict)
    budget: dict[int, mathopt.LinearConstraint] = field(default_factory=dict)

    def started(self, pid: str) -> mathopt.LinearExpression:
        """1 if project `pid` starts in some year of its window, 0 if it is not funded."""
        return mathopt.LinearExpression(sum(self.x[pid, t] for t in self.portfolio.project(pid).starts()))

    def started_by(self, pid: str, year: int) -> mathopt.LinearExpression:
        """1 if project `pid` has started in `year` or earlier."""
        return mathopt.LinearExpression(
            sum(self.x[pid, t] for t in self.portfolio.project(pid).starts() if t <= year))


def groups_of(portfolio: Portfolio) -> dict[str, list[str]]:
    """Alternative group -> its projects, in project order."""
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    return groups


def build(portfolio: Portfolio, *, integer: bool = True, must_do: bool = True, alternatives: bool = True,
          parents: bool = True) -> Plan:
    """The planning model with GridCap's own rules: once, must-do, alternatives, parent and lag, budgets."""
    model = mathopt.Model(name=f"{portfolio.name} plan")
    x = {(p.project_id, t): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}
    plan = Plan(portfolio, model, x)
    for p in portfolio.projects:
        if must_do and p.must_do:
            model.add_linear_constraint(plan.started(p.project_id) == 1, name=f"must_{p.project_id}")
        else:
            model.add_linear_constraint(plan.started(p.project_id) <= 1, name=f"once_{p.project_id}")
    if alternatives:
        for g, members in groups_of(portfolio).items():
            model.add_linear_constraint(sum(plan.started(m) for m in members) <= 1, name=f"alt_{g}")
    if parents:
        for c in portfolio.projects:
            if c.parent:
                add_after(plan, portfolio.project(c.parent), c, c.parent_lag)
    plan.spend = spend_by_year(portfolio, x)
    plan.budget = {y: model.add_linear_constraint(plan.spend[y] <= portfolio.budget[y], name=f"budget_{y}")
                   for y in portfolio.years}
    model.maximize(sum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts()))
    return plan


def add_after(plan: Plan, parent: Project, child: Project, lag: int, name: str = "after") -> None:
    """The child may have started by year t only if the parent had started by t - lag (lesson 6.4.3)."""
    for t in child.starts():
        plan.model.add_linear_constraint(
            plan.started_by(child.project_id, t) <= plan.started_by(parent.project_id, t - lag),
            name=f"{name}_{child.project_id}_{t}")


def spend_by_year(portfolio: Portfolio, x: dict) -> dict[int, mathopt.LinearExpression]:
    """What the plan spends in each calendar year, with each project's cost spread over its life."""
    spend = {y: mathopt.LinearExpression() for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                spend[year] += amount * x[p.project_id, t]
    return spend


def schedule(plan: Plan, result: mathopt.SolveResult) -> dict[str, int]:
    """Project id -> start year, for every project the solution starts."""
    return {pid: t for (pid, t), v in plan.x.items() if result.variable_values(v) > 0.5}


def solve_highs(model: mathopt.Model, params: mathopt.SolveParameters | None = EXACT) -> mathopt.SolveResult:
    """Solve with HiGHS, keeping the engine's stray debug line out of the program's output.

    The HiGHS bundled in OR-Tools 9.15.6755 prints a debug line on some MIP solves with no log
    requested. It is buffered C output, so standard output points at
    /dev/null for the solve and that buffer is flushed before it is restored.
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


def status(result: mathopt.SolveResult) -> str:
    return result.termination.reason.name


def money(value: float) -> str:
    return f"${value:,.0f}k"
