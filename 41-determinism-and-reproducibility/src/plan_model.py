"""The GridCap multi-period plan that every program of this module solves, in MathOpt and in CP-SAT.

GridCap is a fictional utility's portfolio. The model is lesson 6.4.1's timing model: one binary
x[i, t] per project and allowed start year, once and must-do rows, alternative groups, cumulative
precedence with lags, and one budget row per year; the objective is NPV by start year.

`order` is the order in which the projects' variables and rows are added. The model is the same
set of rows whatever the order, but the solver sees its columns and rows in that order, and lesson
10.2.1 shows what that does to the plan it returns.
"""

from __future__ import annotations

import ctypes
import hashlib
import os
import sys
from dataclasses import dataclass

from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

from gridcap import Portfolio


@dataclass
class Plan:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]          # x[i, t] = 1: project i starts in year t


def ordered(portfolio: Portfolio, order: list[str] | None):
    """The portfolio's projects in the given order (default: the portfolio's own order)."""
    by_id = {p.project_id: p for p in portfolio.projects}
    return [by_id[i] for i in order] if order is not None else list(portfolio.projects)


def weight(project, start: int, objective: str) -> int:
    """The objective coefficient of x[i, t]: its NPV in $k, or 1 for every start when counting."""
    if objective == "npv":
        return project.npv[start]
    if objective == "count":
        return 1
    raise ValueError(objective)


def build(portfolio: Portfolio, order: list[str] | None = None, objective: str = "npv") -> Plan:
    """The timing model in MathOpt, with columns and rows added in `order`.

    `objective` is "npv" (the NPV of the plan, $k) or "count" (how many projects start).
    """
    projects = ordered(portfolio, order)
    by_id = {p.project_id: p for p in projects}
    model = mathopt.Model(name=f"{portfolio.name} plan")
    x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
         for p in projects for t in p.starts()}

    def started(pid: str):
        return sum(x[pid, t] for t in by_id[pid].starts())

    for p in projects:
        if p.must_do:
            model.add_linear_constraint(started(p.project_id) == 1, name=f"must_{p.project_id}")
        else:
            model.add_linear_constraint(started(p.project_id) <= 1, name=f"once_{p.project_id}")
    groups: dict[str, list[str]] = {}
    for p in projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        model.add_linear_constraint(sum(started(m) for m in members) <= 1, name=f"alt_{g}")
    for c in projects:
        if c.parent:
            for t in c.starts():
                model.add_linear_constraint(
                    sum(x[c.project_id, u] for u in c.starts() if u <= t)
                    <= sum(x[c.parent, s] for s in by_id[c.parent].starts() if s <= t - c.parent_lag),
                    name=f"after_{c.project_id}_{t}")
    spend = {y: mathopt.LinearExpression() for y in portfolio.years}
    for p in projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                spend[year] += amount * x[p.project_id, t]
    for y in portfolio.years:
        model.add_linear_constraint(spend[y] <= portfolio.budget[y], name=f"budget_{y}")
    model.maximize(sum(weight(p, t, objective) * x[p.project_id, t] for p in projects for t in p.starts()))
    return Plan(model, x)


def schedule(plan: Plan, result: mathopt.SolveResult) -> dict[str, int]:
    """Project id -> start year, for every project the solution starts."""
    return {pid: t for (pid, t), v in plan.x.items() if result.variable_values(v) > 0.5}


def digest(starts: dict[str, int]) -> str:
    """A fingerprint of a plan: sha256 of its sorted (project, start) pairs, first 12 hex digits."""
    return hashlib.sha256(repr(sorted(starts.items())).encode("utf-8")).hexdigest()[:12]


def solve_highs(model: mathopt.Model, params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
    """Solve with HiGHS, keeping the engine's stray debug line out of the output."""
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


@dataclass
class CpPlan:
    model: cp_model.CpModel
    x: dict[tuple[str, int], cp_model.IntVar]


def build_cpsat(portfolio: Portfolio, order: list[str] | None = None, objective: str = "npv") -> CpPlan:
    """The same timing model in CP-SAT (NPVs and costs are integers in $k, as CP-SAT needs)."""
    projects = ordered(portfolio, order)
    by_id = {p.project_id: p for p in projects}
    model = cp_model.CpModel()
    x = {(p.project_id, t): model.new_bool_var(f"x_{p.project_id}_{t}") for p in projects for t in p.starts()}

    def started(pid: str):
        return sum(x[pid, t] for t in by_id[pid].starts())

    for p in projects:
        model.add(started(p.project_id) == 1 if p.must_do else started(p.project_id) <= 1)
    groups: dict[str, list[str]] = {}
    for p in projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for members in groups.values():
        model.add(sum(started(m) for m in members) <= 1)
    for c in projects:
        if c.parent:
            for t in c.starts():
                model.add(sum(x[c.project_id, u] for u in c.starts() if u <= t)
                          <= sum(x[c.parent, s] for s in by_id[c.parent].starts() if s <= t - c.parent_lag))
    for y in portfolio.years:
        model.add(sum(p.spend(t)[y] * x[p.project_id, t] for p in projects for t in p.starts()
                      if y in p.spend(t)) <= portfolio.budget[y])
    model.maximize(sum(weight(p, t, objective) * x[p.project_id, t] for p in projects for t in p.starts()))
    return CpPlan(model, x)


def schedule_cpsat(plan: CpPlan, solver: cp_model.CpSolver) -> dict[str, int]:
    return {pid: t for (pid, t), v in plan.x.items() if solver.value(v)}
