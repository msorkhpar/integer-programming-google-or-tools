"""The GridCap planning model that this module tests, written one rule per function.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.

The model is the multi-period selection of lessons 6.4.1 and 6.5.1 to 6.5.4: one binary x[i, t]
per project and allowed start year, and five rules, each added by its own function so a test can
build a model with one rule and nothing else:

    once    a discretionary project starts at most once
    must    a must-do project starts exactly once
    alt     at most one project of an alternative group
    after   a child starts only if its parent started at least `lag` years before (cumulative form)
    budget  each year's spend, with every project's cost spread over its years of work, within B_y

`build(portfolio, rules)` takes the rules as a mapping from name to function, so a test can swap
one function for a broken copy and see whether the tests notice.
"""

from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from gridcap import Portfolio


@dataclass
class Built:
    """A built model with its start variables, keyed by (project, start year)."""

    portfolio: Portfolio
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]


def started(built: Built, pid: str) -> mathopt.LinearExpression:
    """1 if project `pid` starts in some year of its window, else 0."""
    total = mathopt.LinearExpression()
    for t in built.portfolio.project(pid).starts():
        total += built.x[pid, t]
    return total


def add_once(built: Built) -> None:
    for p in built.portfolio.projects:
        if not p.must_do:
            built.model.add_linear_constraint(started(built, p.project_id) <= 1, name=f"once_{p.project_id}")


def add_must(built: Built) -> None:
    for p in built.portfolio.projects:
        if p.must_do:
            built.model.add_linear_constraint(started(built, p.project_id) == 1, name=f"must_{p.project_id}")


def add_alt(built: Built) -> None:
    groups: dict[str, list[str]] = {}
    for p in built.portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in sorted(groups.items()):
        total = mathopt.LinearExpression()
        for m in members:
            total += started(built, m)
        built.model.add_linear_constraint(total <= 1, name=f"alt_{g}")


def add_after(built: Built) -> None:
    by_id = {p.project_id: p for p in built.portfolio.projects}
    for c in built.portfolio.projects:
        if not c.parent:
            continue
        parent = by_id[c.parent]
        for t in c.starts():
            child_by_t = mathopt.LinearExpression()
            for u in c.starts():
                if u <= t:
                    child_by_t += built.x[c.project_id, u]
            parent_by = mathopt.LinearExpression()
            for s in parent.starts():
                if s <= t - c.parent_lag:
                    parent_by += built.x[parent.project_id, s]
            built.model.add_linear_constraint(child_by_t <= parent_by, name=f"after_{c.project_id}_{t}")


def spend(built: Built) -> dict[int, mathopt.LinearExpression]:
    """What the plan spends in each calendar year, each project's cost spread over its life."""
    by_year = {y: mathopt.LinearExpression() for y in built.portfolio.years}
    for p in built.portfolio.projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                if year in by_year:
                    by_year[year] += amount * built.x[p.project_id, t]
    return by_year


def add_budget(built: Built) -> None:
    by_year = spend(built)
    for y in built.portfolio.years:
        built.model.add_linear_constraint(by_year[y] <= built.portfolio.budget[y], name=f"budget_{y}")


RULES = {"once": add_once, "must": add_must, "alt": add_alt, "after": add_after, "budget": add_budget}


def build(portfolio: Portfolio, rules: dict | None = None) -> Built:
    """The model with the given rules (all five by default) and the NPV objective."""
    model = mathopt.Model(name=portfolio.name)
    x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}
    built = Built(portfolio, model, x)
    for add in (RULES if rules is None else rules).values():
        add(built)
    model.maximize(sum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts()))
    return built


def accepts(built: Built, starts: set[tuple[str, int]]) -> bool:
    """Does the model accept these starts? Fix every variable, solve, and read the status.

    Each (project, year) in `starts` is fixed to 1 and every other variable to 0, so the solver has
    no choice left: OPTIMAL means the starts meet every row, INFEASIBLE means some row refuses
    them. A start the model has no variable for (outside the window) is refused outright.
    """
    if any(key not in built.x for key in starts):
        return False
    for key, var in built.x.items():
        value = 1.0 if key in starts else 0.0
        var.lower_bound = value
        var.upper_bound = value
    try:
        result = solve_highs(built.model)
    finally:
        for var in built.x.values():
            var.lower_bound, var.upper_bound = 0.0, 1.0
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def allowed(built: Built, plan: dict[str, int]) -> bool:
    """Does the model accept this plan (project -> start year)? See `accepts`."""
    return accepts(built, set(plan.items()))


def schedule(built: Built, result: mathopt.SolveResult) -> dict[str, int]:
    """Project id -> start year, for every project the solution starts, in id order."""
    values = result.variable_values()
    return dict(sorted((pid, t) for (pid, t), v in built.x.items() if values[v] > 0.5))


def solve_highs(model: mathopt.Model, params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
    """Solve with HiGHS, keeping the engine's stray debug line out of the program's output.

    The HiGHS bundled in OR-Tools 9.15.6755 prints a `HighsMipSolverData::...` line on some MIP
    solves with no log requested. It is buffered C output, so standard output
    points at /dev/null for the solve and that buffer is flushed there, as lessons 6.4.1 to 6.4.4 do.
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


EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


def optimize(portfolio: Portfolio, rules: dict | None = None) -> tuple[str, float, dict[str, int]]:
    """Solve to proven optimality: (termination reason, objective, plan)."""
    built = build(portfolio, rules)
    result = solve_highs(built.model, EXACT)
    reason = result.termination.reason
    if reason != mathopt.TerminationReason.OPTIMAL:
        return reason.name, float("nan"), {}
    return reason.name, result.objective_value(), schedule(built, result)
