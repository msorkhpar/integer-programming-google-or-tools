"""GridCap's five-year selection with a bridge loan per year, built in the units you choose.

Each year the plan may overspend its budget by borrowing, up to a credit line of 10% of the
year's budget. Borrowing in a year costs a fixed arrangement fee of $300k plus 5% of the amount.
"Borrow only if the loan is arranged" is a switched row with a big-M, as in lesson 6.2.1.

The model is built in three variants that differ only in their units and their M:

* `TIGHT`: every amount in $k, and M is the credit line, the smallest valid M.
* `HUGE_M`: every amount in $k, and M = 1e9.
* `MIXED`: the objective in dollars, the budget rows and the loan in $M, and M = 1e9.

The fee, the interest rate and the credit line are this module's own parameters; GridCap has
none. GridCap is fictional: its numbers are teaching data.
"""

from __future__ import annotations

import ctypes
import math
import os
import re
import sys
from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from gridcap import Portfolio

FEE = 300            # $k to arrange a loan in one year
RATE = 0.05          # interest, per $k borrowed
CREDIT_SHARE = 10    # the credit line is 1/10 of the year's budget


@dataclass(frozen=True)
class Units:
    """How many of the model's units make $1k: 1000 for dollars, 1 for $k, 0.001 for $M."""

    objective: float
    rows: float
    big_m: float | None          # None: the credit line, the tightest valid M
    name: str


TIGHT = Units(objective=1, rows=1, big_m=None, name="tight ($k, M = credit line)")
HUGE_M = Units(objective=1, rows=1, big_m=1e9, name="huge M ($k, M = 1e9)")
MIXED = Units(objective=1000, rows=0.001, big_m=1e9, name="mixed ($ objective, $M rows, M = 1e9)")


@dataclass
class LoanModel:
    model: mathopt.Model
    units: Units
    x: dict[str, mathopt.Variable]          # x[i] = 1: project i is funded
    loan: dict[int, mathopt.Variable]       # amount borrowed in year y, in the rows' unit
    take: dict[int, mathopt.Variable]       # take[y] = 1: a loan is arranged in year y
    spend: dict[int, mathopt.LinearExpression]

    def in_k(self, objective_value: float) -> float:
        """The objective in $k, whatever unit the model was built in."""
        return objective_value / self.units.objective


def spend_in(project, year: int) -> int:
    """What a project spends in `year` if it starts at its earliest start, in $k."""
    return project.spend(project.earliest_start).get(year, 0)


def credit_line(portfolio: Portfolio, year: int) -> int:
    return portfolio.budget[year] // CREDIT_SHARE


def build(portfolio: Portfolio, units: Units = TIGHT) -> LoanModel:
    o, r = units.objective, units.rows
    model = mathopt.Model(name="loan")
    x = {p.project_id: model.add_binary_variable(name=f"x_{p.project_id}") for p in portfolio.projects}
    loan = {y: model.add_variable(lb=0, name=f"loan_{y}") for y in portfolio.years}
    take = {y: model.add_binary_variable(name=f"take_{y}") for y in portfolio.years}
    # One unit of loan is 1/r $k, so its interest is RATE / r $k, or RATE * o / r objective units.
    model.maximize(sum(p.value * o * x[p.project_id] for p in portfolio.projects)
                   - sum(FEE * o * take[y] + RATE * o / r * loan[y] for y in portfolio.years))
    spend = {}
    for y in portfolio.years:
        spend[y] = sum(spend_in(p, y) * r * x[p.project_id] for p in portfolio.projects if spend_in(p, y))
        model.add_linear_constraint(spend[y] <= portfolio.budget[y] * r + loan[y], name=f"budget_{y}")
        model.add_linear_constraint(loan[y] <= credit_line(portfolio, y) * r, name=f"credit_{y}")
        big_m = credit_line(portfolio, y) * r if units.big_m is None else units.big_m
        model.add_linear_constraint(loan[y] <= big_m * take[y], name=f"switch_{y}")
    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name=f"must_{p.project_id}")
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent], name=f"after_{p.project_id}")
    return LoanModel(model, units, x, loan, take, spend)


# ---------------------------------------------------------------------------------------------
# Solving quietly, with or without the log

TIMES = [
    (re.compile(r"(\s)\d+(\.\d+)?s$"), r"\1<t>s"),                      # HiGHS presolve rounds, progress rows
    (re.compile(r"^(\s*Timing\s+)[\d.]+"), r"\1<t>"),                    # HiGHS report: wall-clock seconds
    (re.compile(r"^(\s*P-D integral\s+)[\d.e+-]+"), r"\1<t>"),           # HiGHS report: changes from run to run
    (re.compile(r"^(Solving Time \(sec\) :).*"), r"\1 <t>"),             # SCIP report
]


def mask_times(line: str) -> str:
    for pattern, replacement in TIMES:
        line = pattern.sub(replacement, line)
    return line


def solve(model: mathopt.Model, solver: mathopt.SolverType = mathopt.SolverType.HIGHS,
          params: mathopt.SolveParameters | None = None) -> tuple[mathopt.SolveResult, list[str]]:
    """Solve and keep the solver's log as a list of lines, with wall-clock times masked.

    Standard output points at /dev/null during the solve: the HiGHS bundled with OR-Tools 9.15
    prints a stray debug line on some MIP solves, even with no log requested. The log itself arrives
    through `msg_cb`. HiGHS ends every log with a line about its deprecated `setLogCallback`,
    which says nothing about the model, so it is dropped.
    """
    lines: list[str] = []
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        result = mathopt.solve(model, solver, params=params, msg_cb=lines.extend)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)
    return result, [mask_times(line) for line in lines if "setLogCallback" not in line]


EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)
NO_PRESOLVE = mathopt.SolveParameters(relative_gap_tolerance=0.0, presolve=mathopt.Emphasis.OFF)


# ---------------------------------------------------------------------------------------------
# Measuring a model's numbers and a solution's violations


def coefficient_ranges(model: mathopt.Model) -> dict[str, tuple[float, float]]:
    """Smallest and largest absolute value of each kind of number, as HiGHS's log reports them.

    Zeros and infinite values are left out, and so are bounds of 0: a binary's bounds [0, 1]
    contribute 1.
    """
    def finite(values):
        return [abs(v) for v in values if v != 0 and math.isfinite(v)]

    kinds = {
        "Matrix": finite(c for row in model.linear_constraints()
                         for c in (row.get_coefficient(v) for v in model.row_nonzeros(row))),
        "Cost": finite(model.objective.get_linear_coefficient(v) for v in model.variables()),
        "Bound": finite(b for v in model.variables() for b in (v.lower_bound, v.upper_bound)),
        "RHS": finite(b for row in model.linear_constraints() for b in (row.lower_bound, row.upper_bound)),
    }
    return {kind: (min(values), max(values)) for kind, values in kinds.items() if values}


def row_violations(model: mathopt.Model, values: dict) -> dict[str, float]:
    """How far each row's activity is outside its bounds at `values`, for the rows that are."""
    broken = {}
    for row in model.linear_constraints():
        activity = sum(row.get_coefficient(v) * values[v] for v in model.row_nonzeros(row))
        over = max(row.lower_bound - activity, activity - row.upper_bound)
        if over > 0:
            broken[row.name] = over
    return broken
