"""Lesson 9.1.1: turn a termination into one of five verdicts, and separate INFEASIBLE_OR_UNBOUNDED.

`verdict` reads a result. `separate` settles an INFEASIBLE_OR_UNBOUNDED answer with a second solve
of a copy whose objective is zero: a model with no objective cannot be unbounded, so that solve
answers only "is there any plan at all?". `runaway` names the variables of an unbounded model that
grow without limit, by capping every unbounded variable at a large number on a copy and reading
which ones end at the cap.
"""

from __future__ import annotations

import math

from ortools.math_opt.python import mathopt

from lock_model import solve

R = mathopt.TerminationReason


def verdict(result: mathopt.SolveResult) -> str:
    """'optimal', 'feasible' (a plan, not proven best), 'infeasible', 'unbounded', or 'unknown'."""
    reason = result.termination.reason
    if reason == R.OPTIMAL:
        return "optimal"
    if reason == R.INFEASIBLE:
        return "infeasible"
    if reason == R.UNBOUNDED:
        return "unbounded"
    if reason == R.INFEASIBLE_OR_UNBOUNDED:
        return "infeasible or unbounded"
    if result.has_primal_feasible_solution():
        return "feasible"
    return "unknown"                                    # a limit stopped the solve before any plan


def copy(model: mathopt.Model) -> mathopt.Model:
    """An independent copy; the caller's model is never edited."""
    return mathopt.Model.from_model_proto(model.export_model())


def separate(model: mathopt.Model, solver: mathopt.SolverType = mathopt.SolverType.HIGHS) -> str:
    """Solve; if the answer is 'infeasible or unbounded', ask a zero-objective copy which it is."""
    first = verdict(solve(model, solver))
    if first != "infeasible or unbounded":
        return first
    feasibility = copy(model)
    feasibility.objective.clear()                       # minimize 0: every plan is optimal, none unbounded
    second = verdict(solve(feasibility, solver))
    return {"optimal": "unbounded", "infeasible": "infeasible"}.get(second, "unknown")


def runaway(model: mathopt.Model, cap: float = 1e7,
            solver: mathopt.SolverType = mathopt.SolverType.HIGHS) -> list[str]:
    """Names of the variables that reach `cap` once every variable with no upper bound gets that bound."""
    capped = copy(model)
    free = [v for v in capped.variables() if math.isinf(v.upper_bound)]
    for v in free:
        v.upper_bound = cap
    result = solve(capped, solver)
    values = result.variable_values()
    return sorted(v.name for v in free if values[v] >= cap - 1e-6)
