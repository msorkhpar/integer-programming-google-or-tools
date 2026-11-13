"""The module's running model: GridCap's one-period project selection under one capital budget.

GridCap is a fictional utility. The selection is lesson 1.1.3's model on the small portfolio: fund
each project or not, keep within the budget, fund every must-do, fund a child only with its parent,
and fund at most one project of each alternative group.

Lesson 9.2.2 adds a routine line-clearance program that money can buy in any amount, a continuous
variable. Its return (CLEARANCE_RATE) and its crew limit (CLEARANCE_CAP) are this module's own
assumptions, not GridCap data.
"""

from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from gridcap import Portfolio

CLEARANCE_RATE = 0.25    # $k of NPV per $k spent on routine line clearance (this module's assumption)
CLEARANCE_CAP = 800      # $k of clearance the crews can deliver (this module's assumption)
EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


@dataclass
class Selection:
    model: mathopt.Model
    x: dict[str, mathopt.Variable]            # x[i] = 1: project i is funded
    budget: mathopt.LinearConstraint
    cost: mathopt.LinearBase                  # what the funded projects cost, $k
    value: mathopt.LinearBase                 # their NPV, $k
    clearance: mathopt.Variable | None = None
    clearance_cap: mathopt.LinearConstraint | None = None


def build(portfolio: Portfolio, budget: float, *, integer: bool = True, clearance: bool = False) -> Selection:
    model = mathopt.Model(name=f"{portfolio.name} selection")
    x = {p.project_id: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}")
         for p in portfolio.projects}
    cost = sum(p.capex * x[p.project_id] for p in portfolio.projects)
    value = sum(p.value * x[p.project_id] for p in portfolio.projects)
    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name=f"must_{p.project_id}")
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent], name=f"parent_{p.project_id}")
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        model.add_linear_constraint(sum(x[i] for i in members) <= 1, name=f"alt_{g}")
    if not clearance:
        row = model.add_linear_constraint(cost <= budget, name="budget")
        model.maximize(value)
        return Selection(model, x, row, cost, value)
    y = model.add_variable(lb=0, name="clearance")          # $k of routine line clearance bought
    cap = model.add_linear_constraint(y <= CLEARANCE_CAP, name="clearance_cap")
    row = model.add_linear_constraint(cost + y <= budget, name="budget")
    model.maximize(value + CLEARANCE_RATE * y)
    return Selection(model, x, row, cost, value, y, cap)


def solve_highs(model: mathopt.Model) -> mathopt.SolveResult:
    """Solve with HiGHS to a zero gap, keeping the engine's stray debug line out of the output.

    The HiGHS bundled in OR-Tools 9.15.6755 prints `HighsMipSolverData::transformNewIntegerFeasible
    Solution tmpSolver.run();` on some MIP solves, as buffered C output. The
    process's standard output points at /dev/null for the solve, and that buffer is flushed there.
    """
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(model, mathopt.SolverType.HIGHS, params=EXACT)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


def solve_glop(model: mathopt.Model) -> mathopt.SolveResult:
    """Solve an LP with GLOP and insist on an optimum that carries dual values."""
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL or not result.has_dual_feasible_solution():
        raise RuntimeError(f"{model.name}: {result.termination.reason.name}")
    return result


def best_value(portfolio: Portfolio, budget: float) -> int | None:
    """V(B): the best NPV the selection reaches with budget B, or None when no plan fits."""
    result = solve_highs(build(portfolio, budget).model)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None
    return round(result.objective_value())


def funded(sel: Selection, result: mathopt.SolveResult) -> list[str]:
    return sorted(pid for pid, v in sel.x.items() if result.variable_values(v) > 0.5)


def clean(number: float, digits: int = 4) -> float:
    """Round for printing, and turn the solver's -0.0 into 0.0."""
    return round(number, digits) + 0.0


def row(model: mathopt.Model, name: str) -> mathopt.LinearConstraint:
    """The linear constraint called `name`."""
    return next(c for c in model.linear_constraints() if c.name == name)


def slack(constraint: mathopt.LinearConstraint, result: mathopt.SolveResult) -> float:
    """How far the row's activity sits from its nearest finite bound: 0 means the row binds."""
    activity = sum(t.coefficient * result.variable_values(t.variable) for t in constraint.terms())
    return min(constraint.upper_bound - activity, activity - constraint.lower_bound)
