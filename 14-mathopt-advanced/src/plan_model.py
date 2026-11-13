"""The GridCap timing model this module extends, plus two helpers every lesson uses.

`build` writes the multi-period selection model of lesson 6.4.1 (start-year binaries, spend spread
over each project's years, cumulative precedence) and keeps a handle on every row, so that later
lessons can edit, delete or re-solve without building again. `refusal` digs out the reason a
solver gives for refusing a model, which OR-Tools 9.15 hides behind an AttributeError. `quiet` keeps
stray C-level output of the bundled solvers off the program's output.
"""

from __future__ import annotations

import contextlib
import ctypes
import os
import sys
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from gridcap import Portfolio

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


@dataclass
class PlanModel:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]            # x[i, t] = 1: project i starts in year t
    spend: dict[int, mathopt.LinearExpression] = field(default_factory=dict)
    budget: dict[int, mathopt.LinearConstraint] = field(default_factory=dict)
    once: dict[str, mathopt.LinearConstraint] = field(default_factory=dict)   # once_i or must_i
    npv: mathopt.LinearExpression = field(default_factory=mathopt.LinearExpression)

    def started(self, pid: str) -> mathopt.LinearExpression:
        """1 if project `pid` starts in any year, else 0."""
        return mathopt.fast_sum(v for (p, _), v in self.x.items() if p == pid)


def build(portfolio: Portfolio) -> PlanModel:
    model = mathopt.Model(name=f"{portfolio.name} plan")
    x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}
    pm = PlanModel(model, x)
    by_id = {p.project_id: p for p in portfolio.projects}
    for p in portfolio.projects:
        if p.must_do:
            pm.once[p.project_id] = model.add_linear_constraint(pm.started(p.project_id) == 1,
                                                                name=f"must_{p.project_id}")
        else:
            pm.once[p.project_id] = model.add_linear_constraint(pm.started(p.project_id) <= 1,
                                                                name=f"once_{p.project_id}")
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        model.add_linear_constraint(sum(pm.started(m) for m in members) <= 1, name=f"alt_{g}")
    for c in portfolio.projects:
        if c.parent:
            parent = by_id[c.parent]
            for t in c.starts():
                model.add_linear_constraint(
                    sum(x[c.project_id, u] for u in c.starts() if u <= t)
                    <= sum(x[parent.project_id, s] for s in parent.starts() if s <= t - c.parent_lag),
                    name=f"after_{c.project_id}_{t}")
    pm.spend = {y: mathopt.LinearExpression() for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                if year in pm.spend:
                    pm.spend[year] += amount * x[p.project_id, t]
    pm.budget = {y: model.add_linear_constraint(pm.spend[y] <= portfolio.budget[y], name=f"budget_{y}")
                 for y in portfolio.years}
    pm.npv = mathopt.fast_sum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts())
    model.maximize(pm.npv)
    return pm


def plan(pm: PlanModel, values: dict) -> dict[str, int]:
    """Project id -> start year, read from a variable-value dict (a result's or a callback's)."""
    return {pid: t for (pid, t), v in pm.x.items() if values.get(v, 0.0) > 0.5}


def refusal(error: BaseException) -> str:
    """The solver's own reason for an error: OR-Tools 9.15 raises an AttributeError whose
    `__context__` holds the real error, a StatusNotOk. Its text is the solver's message followed by
    the status code's name in brackets. Falls back to the error itself."""
    inner = error.__context__ or error.__cause__
    return str(inner if inner is not None else error)


@contextlib.contextmanager
def quiet():
    """Point standard output at /dev/null while a solve runs, then flush the C buffer there.

    The HiGHS bundled with OR-Tools 9.15 prints a stray debug line on some MIP solves, with no log
    requested. Solver logs that a program wants go through `msg_cb` instead.
    """
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        yield
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


def solve(model: mathopt.Model, solver: mathopt.SolverType = mathopt.SolverType.HIGHS, **kwargs) -> mathopt.SolveResult:
    """`mathopt.solve` with stray output suppressed; every keyword argument passes through."""
    kwargs.setdefault("params", EXACT)
    with quiet():
        return mathopt.solve(model, solver, **kwargs)
