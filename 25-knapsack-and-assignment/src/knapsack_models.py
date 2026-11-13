"""The GridCap pieces module 25's programs share: knapsack rows, the selection model, crews, a quiet solve.

GridCap is a fictional utility's portfolio. The crews, their capacities and their rates are invented
for this module's lessons; no number here describes a real utility.
"""

from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from gridcap import Portfolio, Project


# ---------------------------------------------------------------------------------------------
# Knapsack rows (lessons 6.3.1 and 6.3.3)


@dataclass(frozen=True)
class Row:
    """One capacity row: sum of weight[i] * x[i] over the items is at most capacity."""

    name: str
    weight: dict[str, int]      # item -> what it uses of this row's resource ($k)
    capacity: int               # what is left of the resource after the must-do projects ($k)


def discretionary(portfolio: Portfolio) -> list[Project]:
    """The projects that compete: every project that is not a must-do."""
    return [p for p in portfolio.projects if not p.must_do]


def must_do(portfolio: Portfolio) -> list[Project]:
    return [p for p in portfolio.projects if p.must_do]


def capital_row(portfolio: Portfolio) -> Row:
    """The capital budget, with the must-do projects paid for first (lesson 3.2.4)."""
    left = portfolio.capital_budget - sum(p.capex for p in must_do(portfolio))
    return Row("capital", {p.project_id: p.capex for p in discretionary(portfolio)}, left)


def year_rows(portfolio: Portfolio) -> list[Row]:
    """One row per year: what each project spends that year if it starts as early as it can."""
    rows = []
    for year in portfolio.years:
        must = sum(p.spend(p.earliest_start).get(year, 0) for p in must_do(portfolio))
        weight = {p.project_id: p.spend(p.earliest_start)[year] for p in discretionary(portfolio)
                  if year in p.spend(p.earliest_start)}
        rows.append(Row(f"budget_{year}", weight, portfolio.budget[year] - must))
    return rows


def knapsack_model(values: dict[str, int], rows: list[Row], *, integer: bool = True):
    """max sum v_i x_i subject to every row; integer=False gives the LP relaxation (0 <= x <= 1)."""
    model = mathopt.Model(name="knapsack")
    x = {i: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{i}") for i in values}
    for row in rows:
        model.add_linear_constraint(sum(w * x[i] for i, w in row.weight.items()) <= row.capacity, name=row.name)
    model.maximize(sum(v * x[i] for i, v in values.items()))
    return model, x


def chosen(x: dict, result: mathopt.SolveResult) -> list:
    """The keys whose variable is 1 in the solution, in the dictionary's order."""
    return [key for key, var in x.items() if result.variable_values(var) > 0.5]


# ---------------------------------------------------------------------------------------------
# The selection model of lesson 1.1.1 (module 23 builds the same one)


def selection(portfolio: Portfolio):
    """One binary per project; the capital budget and the must-do, parent and alternative rows."""
    model = mathopt.Model(name=f"{portfolio.name} selection")
    y = {p.project_id: model.add_binary_variable(name=f"y_{p.project_id}") for p in portfolio.projects}
    model.add_linear_constraint(sum(p.capex * y[p.project_id] for p in portfolio.projects)
                                <= portfolio.capital_budget, name="budget")
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(y[p.project_id] == 1, name=f"must_{p.project_id}")
        if p.parent:
            model.add_linear_constraint(y[p.project_id] <= y[p.parent], name=f"parent_{p.project_id}")
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        model.add_linear_constraint(sum(y[i] for i in members) <= 1, name=f"alt_{g}")
    model.maximize(sum(p.value * y[p.project_id] for p in portfolio.projects))
    return model, y


def base_plan(portfolio: Portfolio) -> list[Project]:
    """The best plan of the selection model: on GridCap small, 20 projects worth $25,336k."""
    model, y = selection(portfolio)
    result = solve_highs(model, EXACT)
    return [portfolio.project(i) for i in chosen(y, result)]


# ---------------------------------------------------------------------------------------------
# Crews (lesson 6.3.2). Invented for the lesson: four regional crews and one contractor.

CREWS = ("Ridge", "Valley", "Coast", "Plains")       # each crew is based in the region of its name
CONTRACTOR = "Contractor"
CAPACITY = {"Ridge": 30, "Valley": 30, "Coast": 20, "Plains": 20, CONTRACTOR: 20}   # crew-months
RATE = {"Ridge": 20, "Valley": 20, "Coast": 20, "Plains": 20, CONTRACTOR: 35}       # $k per crew-month
TRAVEL = 1                                          # crew-months a regional crew loses away from home
LINE_CREWS = ("Ridge", "Valley", CONTRACTOR)        # the crews qualified for transmission work


def size(p: Project, crew: str) -> int:
    """Crew-months project p takes if `crew` does it: one more for a regional crew away from home."""
    away = crew != CONTRACTOR and crew != p.region
    return p.crew_months + (TRAVEL if away else 0)


def cost(p: Project, crew: str) -> int:
    """What project p's labour costs if `crew` does it, in $k."""
    return RATE[crew] * size(p, crew)


def eligible(p: Project, crew: str) -> bool:
    return p.program != "transmission" or crew in LINE_CREWS


def assignment_model(plan: list[Project], *, only_eligible: bool = False, integer: bool = True):
    """Every project of the plan to exactly one crew, within each crew's capacity, at least labour cost."""
    model = mathopt.Model(name="crew assignment")
    crews = CREWS + (CONTRACTOR,)
    x = {(p.project_id, k): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}_{k}")
         for p in plan for k in crews if not only_eligible or eligible(p, k)}
    for p in plan:
        model.add_linear_constraint(
            sum(x[p.project_id, k] for k in crews if (p.project_id, k) in x) == 1, name=f"assign_{p.project_id}")
    for k in crews:
        model.add_linear_constraint(
            sum(size(p, k) * x[p.project_id, k] for p in plan if (p.project_id, k) in x) <= CAPACITY[k],
            name=f"capacity_{k}")
    model.minimize(sum(cost(p, k) * var for (i, k), var in x.items() for p in plan if p.project_id == i))
    return model, x


# ---------------------------------------------------------------------------------------------
# Solving


EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


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
