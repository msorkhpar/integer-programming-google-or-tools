"""GridCap's multi-period model with work fronts, written in a weak or a strong form, and the measuring tools.

The model is lesson 6.4.1's: one binary x[i, t] per project and allowed start year, must-do,
alternative and precedence rows, and a budget row per year. Module 29 adds **work fronts**: a
region's program (Ridge distribution, Coast transmission, ...) must be mobilized before any of its
projects can start, at a one-off fee. "No project of a front starts unless the front is mobilized"
is the rule written two ways, `aggregated` (one row per front) and `disaggregated` (one row per
project). Optional **crew rows** cap each program's crew-months per year (module 24's reading of
GridCap's `crews`).

The fee is this module's own parameter, 10% of the front's total capex; GridCap itself has none.
GridCap is fictional.
"""

from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from gridcap import PROGRAMS, Portfolio

FEE_SHARE = 0.10            # a front's mobilization fee, as a share of its projects' total capex
EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


@dataclass
class StrongModel:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]          # x[i, t] = 1: project i starts in year t
    front: dict[tuple[str, str], mathopt.Variable] = field(default_factory=dict)   # front[r, g] = 1: mobilized
    fee: dict[tuple[str, str], int] = field(default_factory=dict)


def fronts_of(portfolio: Portfolio) -> dict[tuple[str, str], list[str]]:
    """Work front (region, program) -> the projects in it."""
    fronts: dict[tuple[str, str], list[str]] = {}
    for p in portfolio.projects:
        fronts.setdefault((p.region, p.program), []).append(p.project_id)
    return fronts


def front_fee(portfolio: Portfolio, members: list[str]) -> int:
    return 10 * int(FEE_SHARE * sum(portfolio.project(i).capex for i in members) // 10)


def active(project, t: int, year: int) -> bool:
    """Is a project that starts in year t being worked on in `year`?"""
    return t <= year < t + project.duration


def build(portfolio: Portfolio, *, integer: bool = True, fronts: str | None = "disaggregated",
          precedence: str = "cumulative", crews: bool = False) -> StrongModel:
    """The timing model of lesson 6.4.1, plus work fronts in the form asked for (None: no fronts)."""
    model = mathopt.Model(name=f"{portfolio.name} strong")
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
            add_precedence(model, x, by_id[c.parent], c, precedence)
    for year in portfolio.years:
        spend = sum(amount * x[p.project_id, t] for p in portfolio.projects for t in p.starts()
                    for y, amount in p.spend(t).items() if y == year)
        model.add_linear_constraint(spend <= portfolio.budget[year], name=f"budget_{year}")
    if crews:
        for g in PROGRAMS:
            for year in portfolio.years:
                use = sum(p.crew_months * x[p.project_id, t] for p in portfolio.projects if p.program == g
                          for t in p.starts() if active(p, t, year))
                model.add_linear_constraint(use <= portfolio.crews[g, year], name=f"crews_{g}_{year}")

    sm = StrongModel(model, x)
    value = sum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts())
    if fronts is not None:
        for (region, program), members in fronts_of(portfolio).items():
            y = model.add_variable(lb=0, ub=1, is_integer=integer, name=f"front_{region}_{program}")
            sm.front[region, program] = y
            sm.fee[region, program] = front_fee(portfolio, members)
            add_front(model, y, [started(i) for i in members], members, f"{region}_{program}", fronts)
        value -= sum(sm.fee[k] * sm.front[k] for k in sm.front)
    model.maximize(value)
    return sm


def add_front(model, y, started: list, members: list[str], name: str, form: str) -> None:
    """No project of the front starts unless the front is mobilized (y = 1)."""
    if form == "aggregated":
        # One row: the number of projects started is at most the front's size, and 0 if y = 0.
        model.add_linear_constraint(sum(started) <= len(started) * y, name=f"front_{name}")
    elif form == "disaggregated":
        # One row per project: this project starts only if y = 1.
        for pid, s in zip(members, started):
            model.add_linear_constraint(s <= y, name=f"front_{name}_{pid}")
    else:
        raise ValueError(form)


def add_precedence(model, x, parent, child, form: str) -> None:
    """The child starts only if the parent does, at least `child.parent_lag` years after it (lesson 6.4.3)."""
    lag = child.parent_lag
    if form == "aggregated":
        model.add_linear_constraint(sum(x[child.project_id, t] for t in child.starts())
                                    <= sum(x[parent.project_id, s] for s in parent.starts()),
                                    name=f"needs_{child.project_id}")
        big = max(parent.starts()) + lag
        model.add_linear_constraint(
            sum(t * x[child.project_id, t] for t in child.starts())
            >= sum((s + lag) * x[parent.project_id, s] for s in parent.starts())
            - big * (1 - sum(x[child.project_id, t] for t in child.starts())),
            name=f"after_{child.project_id}")
    elif form == "cumulative":
        for t in child.starts():
            model.add_linear_constraint(
                sum(x[child.project_id, u] for u in child.starts() if u <= t)
                <= sum(x[parent.project_id, s] for s in parent.starts() if s <= t - lag),
                name=f"after_{child.project_id}_{t}")
    else:
        raise ValueError(form)


def size(model: mathopt.Model) -> tuple[int, int]:
    """(variables, rows)."""
    return sum(1 for _ in model.variables()), sum(1 for _ in model.linear_constraints())


def lp_bound(model: mathopt.Model) -> mathopt.SolveResult:
    """Solve the model as given with GLOP; build it with integer=False to get its LP relaxation."""
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        raise RuntimeError(f"LP not solved: {result.termination}")
    return result


def solve_highs(model: mathopt.Model, params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
    """Solve with HiGHS, keeping the engine's stray debug line out of the program's output.

    The HiGHS bundled in OR-Tools 9.15.6755 prints a debug line on some MIP solves with no log
    requested. Standard output points at /dev/null for the solve, and the C
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


def root_bound(model: mathopt.Model) -> float:
    """HiGHS's bound after its root node: the LP after presolve and the solver's own cuts."""
    result = solve_highs(model, mathopt.SolveParameters(relative_gap_tolerance=0.0, node_limit=1))
    return result.best_objective_bound()


def gap_closed(weak: float, strong: float, optimum: float) -> float:
    """The share of the weak formulation's integrality gap that the strong one closes."""
    return (weak - strong) / (weak - optimum)
