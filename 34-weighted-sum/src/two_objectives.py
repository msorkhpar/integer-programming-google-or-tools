"""GridCap's two objectives, NPV and risk removed, on the start-year model of lessons 6.4.1-6.4.2.

The risk coefficients and the model builder are copied from module 32 (`asset_curves.py` and
`risk_model.py`, lesson 7.3.4) so that this module runs on its own. The one change: `build` adds no
objective, and `npv_of` and `risk_of` return the two objective expressions, so each lesson decides
how to combine them.
"""

from __future__ import annotations

import ctypes
import math
import os
import sys
from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from gridcap import Portfolio

WINDOW = 10        # years over which a project's risk reduction is counted, from the plan's first year
#: The share of its age an asset keeps after each kind of work (the convention of lesson 1.1.2).
AGE_AFTER = {"replace": 0.0, "rebuild": 0.0, "underground": 0.0, "repair": 0.5, "trim": 0.5,
             "clear": 0.5, "widen": 0.5}


# ---------------------------------------------------------------------------------------------
# The coefficients (lessons 7.2.4 and 7.3.4)


def yearly_risk(age: float, beta: float, eta: float, cof: float) -> float:
    """Expected failure cost in the coming year, $k: CoF times the expected failures at this age."""
    return cof * (((age + 1) / eta) ** beta - (age / eta) ** beta)


def risk_reduction(asset, window, start: int, duration: int, keep: float, rate: float) -> float:
    """Discounted risk removed over `window` by work that starts in `start` (lesson 7.3.4)."""
    first, done = window[0], start + duration
    total = 0.0
    for y in window:
        before = asset.age + (y - first)
        after = before if y < done else keep * (asset.age + (done - first)) + (y - done)
        cut = (yearly_risk(before, asset.weibull_beta, asset.weibull_eta, asset.cof)
               - yearly_risk(after, asset.weibull_beta, asset.weibull_eta, asset.cof))
        total += cut / (1 + rate) ** (y - first)
    return total


def risk_coefficients(portfolio: Portfolio) -> dict[tuple[str, int], float]:
    """rr[i, s]: discounted risk removed over the window if project i starts in year s, $k."""
    window = tuple(range(portfolio.years[0], portfolio.years[0] + WINDOW))
    return {(p.project_id, s): risk_reduction(portfolio.asset(p.asset_id), window, s, p.duration,
                                              AGE_AFTER[p.intervention], portfolio.discount_rate)
            for p in portfolio.projects for s in p.starts()}


def npv_coefficients(portfolio: Portfolio) -> dict[tuple[str, int], int]:
    """npv[i, s]: the NPV of project i started in year s, $k (lesson 7.2.4)."""
    return {(p.project_id, s): p.npv[s] for p in portfolio.projects for s in p.starts()}


# ---------------------------------------------------------------------------------------------
# The model (lesson 6.4.2's rows, no objective)


@dataclass
class StartModel:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]
    npv: dict[tuple[str, int], int]
    rr: dict[tuple[str, int], float]

    def npv_of(self) -> mathopt.LinearExpression:
        return mathopt.LinearExpression() + sum(self.npv[k] * v for k, v in self.x.items())

    def risk_of(self) -> mathopt.LinearExpression:
        return mathopt.LinearExpression() + sum(self.rr[k] * v for k, v in self.x.items())


def build(portfolio: Portfolio, integer: bool = True) -> StartModel:
    """The start-year model with every rule of lesson 6.4.2 and no objective yet.

    With `integer=False` each x[i, t] may take any value in [0, 1]: the LP relaxation.
    """
    model = mathopt.Model(name=f"{portfolio.name} two objectives")
    x = {(p.project_id, t): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}
    by_id = {p.project_id: p for p in portfolio.projects}

    def started(pid: str):
        return sum(x[pid, t] for t in by_id[pid].starts())

    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(started(p.project_id) == 1, name=f"must_{p.project_id}")
        else:
            model.add_linear_constraint(started(p.project_id) <= 1, name=f"once_{p.project_id}")
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        model.add_linear_constraint(sum(started(m) for m in members) <= 1, name=f"alt_{g}")
    for c in portfolio.projects:
        if c.parent:
            parent = by_id[c.parent]
            for t in c.starts():
                model.add_linear_constraint(
                    sum(x[c.project_id, u] for u in c.starts() if u <= t)
                    <= mathopt.LinearExpression() + sum(x[parent.project_id, s] for s in parent.starts()
                                                        if s <= t - c.parent_lag),
                    name=f"after_{c.project_id}_{t}")
    spend = {y: mathopt.LinearExpression() for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                spend[year] += amount * x[p.project_id, t]
    for y in portfolio.years:
        model.add_linear_constraint(spend[y] <= portfolio.budget[y], name=f"budget_{y}")
    return StartModel(model, x, npv_coefficients(portfolio), risk_coefficients(portfolio))


def solve_highs(model: mathopt.Model) -> mathopt.SolveResult:
    """Solve with HiGHS to a zero gap, keeping the engine's stray output away from the program's.

    The HiGHS bundled with OR-Tools 9.15 can print a debug line on some MIP solves even with no log
    requested; it is buffered C output, so standard output points at /dev/null for the solve and the
    C buffer is flushed there.
    """
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(model, mathopt.SolverType.HIGHS,
                             params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


def plan_of(sm: StartModel, result: mathopt.SolveResult) -> dict[str, int]:
    """Project id -> start year, for every project the solution starts."""
    return {pid: t for (pid, t), v in sm.x.items() if result.variable_values(v) > 0.5}


def score(sm: StartModel, plan: dict[str, int]) -> tuple[int, float]:
    """(NPV, risk removed) of a plan, both in $k, computed from the coefficients, not the solver."""
    return sum(sm.npv[k] for k in plan.items()), sum(sm.rr[k] for k in plan.items())


def weighted(sm: StartModel, w_npv: float, w_risk: float) -> dict[str, int]:
    """The plan that maximizes w_npv * NPV + w_risk * risk removed."""
    sm.model.maximize(w_npv * sm.npv_of() + w_risk * sm.risk_of())
    result = solve_highs(sm.model)
    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL, result.termination
    return plan_of(sm, result)


def isclose(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=0, abs_tol=1e-6)
