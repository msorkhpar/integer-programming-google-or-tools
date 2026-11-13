"""GridCap's objectives and the start-year model every lesson of module 35 solves.

The risk coefficients and the model are those of module 32 (lesson 7.3.4), as module 34 copies them,
so that this module runs on its own: `build` writes the rules of lessons 6.4.1-6.4.2 and no
objective, and `StartModel.objective(name)` returns one of three linear expressions, "npv" and
"risk" (both $k, to maximize) and "spend" (total capital spent inside the plan's years, $k).
`solve` runs HiGHS to a chosen gap with its stray output kept off the program's output (the HiGHS
bundled with OR-Tools 9.15 can print a debug line on some MIP solves even with no log requested).
GridCap is a fictional utility's portfolio.
"""

from __future__ import annotations

import contextlib
import ctypes
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


def coefficients(portfolio: Portfolio) -> dict[str, dict[tuple[str, int], float]]:
    """Per start: npv[i, s] (lesson 7.2.4), risk[i, s] (lesson 7.3.4) and spend[i, s], all $k."""
    window = tuple(range(portfolio.years[0], portfolio.years[0] + WINDOW))
    npv, risk, spend = {}, {}, {}
    for p in portfolio.projects:
        for s in p.starts():
            npv[p.project_id, s] = p.npv[s]
            risk[p.project_id, s] = risk_reduction(portfolio.asset(p.asset_id), window, s, p.duration,
                                                   AGE_AFTER[p.intervention], portfolio.discount_rate)
            spend[p.project_id, s] = sum(a for y, a in p.spend(s).items() if y in portfolio.budget)
    return {"npv": npv, "risk": risk, "spend": spend}


# ---------------------------------------------------------------------------------------------
# The model (lesson 6.4.2's rows, no objective)


@dataclass
class StartModel:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]
    coef: dict[str, dict[tuple[str, int], float]]

    def objective(self, name: str) -> mathopt.LinearExpression:
        """The linear expression of objective `name`: "npv", "risk" or "spend"."""
        c = self.coef[name]
        return mathopt.LinearExpression() + mathopt.fast_sum(c[k] * v for k, v in self.x.items())


def build(portfolio: Portfolio) -> StartModel:
    """The start-year model with every rule of lesson 6.4.2 and no objective yet."""
    model = mathopt.Model(name=f"{portfolio.name} lexicographic")
    x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}
    by_id = {p.project_id: p for p in portfolio.projects}

    def started(pid: str):
        return mathopt.LinearExpression() + sum(x[pid, t] for t in by_id[pid].starts())

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
                if year in spend:
                    spend[year] += amount * x[p.project_id, t]
    for y in portfolio.years:
        model.add_linear_constraint(spend[y] <= portfolio.budget[y], name=f"budget_{y}")
    return StartModel(model, x, coefficients(portfolio))


# ---------------------------------------------------------------------------------------------
# Solving and reading


@contextlib.contextmanager
def quiet():
    """Point standard output at /dev/null while a solve runs, then flush the C buffer there.

    The HiGHS bundled with OR-Tools 9.15 can print a buffered debug line on some MIP solves.
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


def solve(model: mathopt.Model, gap: float = 0.0) -> mathopt.SolveResult:
    """HiGHS to a relative gap of `gap` (0 by default: proven optimal), stopping on anything else."""
    with quiet():
        result = mathopt.solve(model, mathopt.SolverType.HIGHS,
                               params=mathopt.SolveParameters(relative_gap_tolerance=gap))
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        raise RuntimeError(f"{model.name}: {result.termination}")
    return result


def plan_of(sm: StartModel, result: mathopt.SolveResult) -> dict[str, int]:
    """Project id -> start year, for every project the solution starts."""
    return {pid: t for (pid, t), v in sm.x.items() if result.variable_values(v) > 0.5}


def score(sm: StartModel, plan: dict[str, int], name: str) -> float:
    """Objective `name` of a plan, summed from the coefficients, not read from the solver."""
    return sum(sm.coef[name][k] for k in plan.items())
