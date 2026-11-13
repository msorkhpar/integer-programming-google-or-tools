"""A reusable two-objective frontier generator for any MathOpt model: ε-constraint and AUGMECON.

Both objectives are linear expressions to be **maximized** (to minimize one, pass its negation).
`first` is the objective each solve maximizes; `second` is the one held at a floor, ε. Nothing here
knows about GridCap: lessons 8.3.1-8.3.3 use it on NPV and risk, and module 38 can use it on value
and budget.

Every solve is HiGHS through MathOpt at a zero relative gap: a frontier point is only as good as
the solve that found it.
"""

from __future__ import annotations

import ctypes
import math
import os
import sys
from dataclasses import dataclass, field
from typing import Mapping

from ortools.math_opt.python import mathopt

TOL = 1e-6     # how far a value may sit below its floor and still count as on it (solver tolerance)
SAME = 1e-3    # objective values closer than this count as equal when comparing plans (solver noise)


@dataclass(frozen=True)
class Point:
    """One plan, scored on both objectives. `values` holds the solver's variable values."""
    first: float
    second: float
    values: Mapping[mathopt.Variable, float] = field(default=None, compare=False, repr=False)


def solve(model: mathopt.Model) -> mathopt.SolveResult:
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


def score(first, second, values) -> Point:
    """The plan's value on both objectives, read from its variable values."""
    return Point(mathopt.evaluate_expression(first, values), mathopt.evaluate_expression(second, values),
                 values)


# ---------------------------------------------------------------------------------------------
# The two ends of the frontier (the payoff table)


def best_of(model, objective, then=None) -> mathopt.SolveResult:
    """Maximize `objective`; with `then`, keep it at its best and maximize `then` as well."""
    model.maximize(objective)
    result = solve(model)
    if then is None or result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return result
    hold = model.add_linear_constraint(objective >= result.objective_value() - TOL, name="hold_best")
    model.maximize(then)
    result = solve(model)
    model.delete_linear_constraint(hold)
    return result


def payoff_table(model, first, second, lexicographic: bool = True) -> tuple[Point, Point]:
    """The plan best on `first` and the plan best on `second`, each scored on both.

    With `lexicographic=True` each end is optimized on its own objective and then, at that value,
    on the other, so neither end can be a weakly efficient plan.
    """
    a = best_of(model, first, second if lexicographic else None)
    b = best_of(model, second, first if lexicographic else None)
    return score(first, second, a.variable_values()), score(first, second, b.variable_values())


# ---------------------------------------------------------------------------------------------
# One ε-constraint solve, plain or augmented


def epsilon_constraint(model, first, second, floor: float) -> Point | None:
    """Plain ε-constraint: maximize `first` subject to `second >= floor`. None if no plan reaches it."""
    row = model.add_linear_constraint(second >= floor, name="eps_floor")
    model.maximize(first)
    result = solve(model)
    model.delete_linear_constraint(row)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None
    return score(first, second, result.variable_values())


def augmecon(model, first, second, floor: float, span: float, rho: float = 1e-3):
    """AUGMECON: maximize first + rho * s / span subject to second - s == floor, s >= 0.

    Returns (point, slack), or None when no plan reaches the floor. `span` is the range of `second`
    over the payoff table, so the reward for slack is at most `rho` whatever the units.
    """
    s = model.add_variable(lb=0.0, name="eps_slack")
    row = model.add_linear_constraint(second - s == floor, name="eps_floor")
    model.maximize(first + (rho / span) * s)
    result = solve(model)
    model.delete_linear_constraint(row)
    model.delete_variable(s)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        return None
    values = result.variable_values()
    return score(first, second, values), values[s]


# ---------------------------------------------------------------------------------------------
# Sweeps


def grid(low: float, high: float, n: int) -> list[float]:
    """n floors evenly spaced from `low` to `high`, both ends included."""
    return [low + (high - low) * k / (n - 1) for k in range(n)]


def exact_frontier(model, first, second, step: float = 1.0, rho: float = 1e-3):
    """Every Pareto-optimal (first, second) pair, when `second` only takes multiples of `step`.

    With integer coefficients on `second` and `step=1` that holds for every plan. The result is exact
    only if, in addition, every solve is optimal and the reward (at most `rho`) is smaller than the
    gap in `first` between any two neighbouring Pareto plans: a fact about the data when `first` is
    not whole numbers, to be checked after the run. Starts the floor at
    the low end of `second` and, after each solve, jumps past every grid floor
    the slack shows would give the same plan (the bypass of AUGMECON2). Stops at the first floor no
    plan reaches. Returns (points, number of ε solves).
    """
    top_first, top_second = payoff_table(model, first, second)
    span = max(top_second.second - top_first.second, step)
    floor, points, solves = math.floor(top_first.second / step + TOL) * step, [], 0
    while floor <= top_second.second + TOL:
        found = augmecon(model, first, second, floor, span, rho)
        solves += 1
        if found is None:
            break                                    # early exit: every higher floor fails too
        point, slack = found
        points.append(point)
        floor += (1 + math.floor(round(slack, 6) / step)) * step
    return points, solves


# ---------------------------------------------------------------------------------------------
# Checking and reading a frontier


def dominates(p: Point, q: Point, tol: float = SAME) -> bool:
    """p is at least as good as q on both objectives and better on one."""
    at_least = p.first >= q.first - tol and p.second >= q.second - tol
    better = p.first > q.first + tol or p.second > q.second + tol
    return at_least and better


def dominated(points: list[Point]) -> list[tuple[Point, Point]]:
    """Every pair (q, p) of the list in which p dominates q. Empty for a true frontier."""
    return [(q, p) for q in points for p in points if dominates(p, q)]


def supported(points: list[Point]) -> list[Point]:
    """The supported points: those on the upper-right convex hull, the only ones a weighted sum can reach.

    A point exactly on the segment between two hull corners is kept: it ties with both ends at that
    segment's price, so it is supported too (lesson 8.1.2's definition and hull test).
    """
    hull: list[Point] = []
    for p in sorted(points, key=lambda p: (p.second, p.first)):
        while len(hull) >= 2:
            a, b = hull[-2], hull[-1]
            if (b.second - a.second) * (p.first - a.first) - (b.first - a.first) * (p.second - a.second) > 1e-9:
                hull.pop()                           # b sits strictly below the segment from a to p
            else:
                break
        hull.append(p)
    return hull
