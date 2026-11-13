"""Turn a season into a plan: which circuits to trim, and in which month, solved by HiGHS through MathOpt."""

from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from vegcrew.data import WEEKS_PER_MONTH, Season

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)
STATUS = {mathopt.TerminationReason.OPTIMAL: "OPTIMAL", mathopt.TerminationReason.FEASIBLE: "FEASIBLE",
          mathopt.TerminationReason.INFEASIBLE: "INFEASIBLE"}


@dataclass(frozen=True)
class Trim:
    cid: str
    month: int                                      # 1 to season.months
    crew: str = ""                                  # stub for lesson 14.1.3
    start: int = 0                                  # stub for lesson 14.1.3
    end: int = 0                                    # stub for lesson 14.1.3


@dataclass(frozen=True)
class Plan:
    status: str                                     # OPTIMAL, FEASIBLE, INFEASIBLE or NOT_SOLVED
    trims: dict[str, Trim] = field(default_factory=dict)
    cost: int = 0                                   # $k spent
    risk_removed: int = 0                           # $k a year of risk the trims remove


def crew_ids(season: Season) -> list[str]:
    """Stub for lesson 14.1.3."""
    return []


def horizon(season: Season) -> int:
    """Stub for lesson 14.1.3."""
    return 0


def build(season: Season) -> tuple[mathopt.Model, dict[tuple[str, int], mathopt.Variable]]:
    model = mathopt.Model(name=f"trim_{season.name}")
    months = range(1, season.months + 1)
    x = {(c.cid, m): model.add_binary_variable(name=f"x_{c.cid}_{m}") for c in season.circuits for m in months}

    def trimmed(cid: str) -> mathopt.LinearExpression:
        return mathopt.fast_sum(x[cid, m] for m in months)

    for c in season.circuits:
        model.add_linear_constraint(trimmed(c.cid) <= 1, name=f"once_{c.cid}")
    for m in months:
        model.add_linear_constraint(
            mathopt.fast_sum(c.weeks * x[c.cid, m] for c in season.circuits) <= season.crews * WEEKS_PER_MONTH,
            name=f"crews_{m}")
    model.add_linear_constraint(mathopt.fast_sum(c.cost * trimmed(c.cid) for c in season.circuits) <= season.budget,
                                name="budget")
    model.maximize(mathopt.fast_sum(c.risk * trimmed(c.cid) for c in season.circuits))
    return model, x


def solve_quietly(model: mathopt.Model) -> mathopt.SolveResult:
    """Solve with HiGHS, keeping its stray C-level debug line off the program's standard output.

    The HiGHS bundled in OR-Tools 9.15 prints `HighsMipSolverData::transformNewIntegerFeasibleSolution`
    on some MIP solves even with no log asked for, and only when the process exits. Standard output
    points at /dev/null for the solve, and the C buffer is flushed there before it is restored.
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


def make_plan(season: Season) -> Plan:
    """Choose the circuits to trim and their months: the most risk removed within the budget and the crews."""
    model, x = build(season)
    result = solve_quietly(model)
    status = STATUS.get(result.termination.reason, result.termination.reason.name)
    if status not in ("OPTIMAL", "FEASIBLE"):
        return Plan(status)
    trims = {cid: Trim(cid, m) for (cid, m), v in x.items() if result.variable_values(v) > 0.5}
    chosen = [season.circuit(cid) for cid in trims]
    return Plan(status, trims, cost=sum(c.cost for c in chosen), risk_removed=sum(c.risk for c in chosen))
