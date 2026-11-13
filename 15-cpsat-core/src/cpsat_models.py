"""The GridCap models module 15 writes in CP-SAT, and the helpers its programs share.

GridCap is a fictional utility's portfolio, generated for this course. `selection` is the model of
lesson 4.4.1: the one-period selection of lesson 1.1.1, a crew-month row per program, and a credit
line drawn in whole tranches. `mathopt_selection` is the same model in MathOpt, so the programs can
check CP-SAT's answer against HiGHS. Nothing here prints.
"""

from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass

from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

from gridcap import PROGRAMS, Portfolio

TRANCHE = 500         # $k of extra capital per credit-line tranche
TRANCHE_COST = 300    # $k that one tranche costs over the plan (interest and fees)
MAX_TRANCHES = 4      # the credit line has four tranches


def crew_need(project) -> int:
    """Crew-months a project needs over its life: its crew-months per year of work, every year."""
    return project.crew_months * project.duration


def crew_capacity(portfolio: Portfolio) -> dict[str, int]:
    """Own crew-months per program over the whole plan: the yearly crews added up."""
    return {g: sum(portfolio.crews[g, y] for y in portfolio.years) for g in PROGRAMS}


def groups_of(portfolio: Portfolio) -> dict[str, list[str]]:
    """Alternative group -> the projects in it."""
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    return groups


@dataclass
class Selection:
    portfolio: Portfolio
    model: cp_model.CpModel
    x: dict[str, cp_model.IntVar]          # x[i] = 1: project i is funded
    k: cp_model.IntVar                     # credit-line tranches drawn, 0..MAX_TRANCHES


def selection(portfolio: Portfolio, *, native: bool = False) -> Selection:
    """The lesson 4.4.1 model in CP-SAT.

    native=False writes the parent and alternative rules as linear rows, as a MILP would;
    native=True writes them as CP-SAT's own logic constraints (lesson 4.4.2). Both allow the same plans.
    """
    model = cp_model.CpModel()
    x = {p.project_id: model.new_bool_var(f"x_{p.project_id}") for p in portfolio.projects}
    k = model.new_int_var(0, MAX_TRANCHES, "tranches")

    model.add(sum(p.capex * x[p.project_id] for p in portfolio.projects)
              <= portfolio.capital_budget + TRANCHE * k).with_name("budget")
    own = crew_capacity(portfolio)
    for g in PROGRAMS:
        model.add(sum(crew_need(p) * x[p.project_id] for p in portfolio.projects if p.program == g)
                  <= own[g]).with_name(f"crews_{g}")
    for p in portfolio.projects:
        if p.must_do:
            model.add(x[p.project_id] == 1).with_name(f"must_{p.project_id}")
        if p.parent and native:
            model.add_implication(x[p.project_id], x[p.parent]).with_name(f"parent_{p.project_id}")
        elif p.parent:
            model.add(x[p.project_id] <= x[p.parent]).with_name(f"parent_{p.project_id}")
    for g, members in groups_of(portfolio).items():
        if native:
            model.add_at_most_one(x[i] for i in members).with_name(f"alt_{g}")
        else:
            model.add(sum(x[i] for i in members) <= 1).with_name(f"alt_{g}")

    model.maximize(sum(p.value * x[p.project_id] for p in portfolio.projects) - TRANCHE_COST * k)
    return Selection(portfolio, model, x, k)


def mathopt_selection(portfolio: Portfolio) -> tuple[mathopt.Model, dict, mathopt.Variable]:
    """The same model in MathOpt, for HiGHS."""
    model = mathopt.Model(name="selection")
    x = {p.project_id: model.add_binary_variable(name=f"x_{p.project_id}") for p in portfolio.projects}
    k = model.add_integer_variable(lb=0, ub=MAX_TRANCHES, name="tranches")
    model.add_linear_constraint(sum(p.capex * x[p.project_id] for p in portfolio.projects)
                                <= portfolio.capital_budget + TRANCHE * k, name="budget")
    own = crew_capacity(portfolio)
    for g in PROGRAMS:
        model.add_linear_constraint(
            sum(crew_need(p) * x[p.project_id] for p in portfolio.projects if p.program == g) <= own[g],
            name=f"crews_{g}")
    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(x[p.project_id] == 1, name=f"must_{p.project_id}")
        if p.parent:
            model.add_linear_constraint(x[p.project_id] <= x[p.parent], name=f"parent_{p.project_id}")
    for g, members in groups_of(portfolio).items():
        model.add_linear_constraint(sum(x[i] for i in members) <= 1, name=f"alt_{g}")
    model.maximize(sum(p.value * x[p.project_id] for p in portfolio.projects) - TRANCHE_COST * k)
    return model, x, k


def one_worker() -> cp_model.CpSolver:
    """A CP-SAT solver on one search worker, so a run repeats exactly (lesson 4.6.3)."""
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    return solver


def funded(sel: Selection, solver: cp_model.CpSolver) -> list[str]:
    """The projects the solver's last solution funds, in portfolio order."""
    return [pid for pid, v in sel.x.items() if solver.boolean_value(v)]


def allowed_assignments(add_rows, names: str) -> list[str]:
    """Every 0/1 assignment of the Booleans `names` that the constraints added by `add_rows` allow.

    `add_rows(model, v)` adds constraints over the Booleans `v[name]`. Each assignment is fixed with
    one equality per Boolean, and CP-SAT is asked whether the model still has a solution. An allowed
    assignment prints as its digits in the order of `names`, so "01" means a = 0 and b = 1.
    """
    found = []
    for n in range(2 ** len(names)):
        values = [(n >> (len(names) - 1 - j)) & 1 for j in range(len(names))]
        model = cp_model.CpModel()
        v = {name: model.new_bool_var(name) for name in names}
        add_rows(model, v)
        for name, value in zip(names, values):
            model.add(v[name] == value)
        if one_worker().solve(model) == cp_model.OPTIMAL:
            found.append("".join(map(str, values)))
    return found


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


EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)
