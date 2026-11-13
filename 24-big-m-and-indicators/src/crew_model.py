"""GridCap's multi-period model with in-house crews and a contractor that can be hired per program and year.

A project needs `crew_months` crew-months in every year it is worked on. Each program has
`crews[(program, year)]` crew-months in house. A program may use more than that in a year only if
it hires a contractor for that year, which costs a fee. "Use more crews only if hired" is the
switched row this module writes with a big-M, with an indicator, and in CP-SAT.

The fee is this module's own parameter; GridCap itself has none. GridCap is fictional.
"""

from __future__ import annotations

import ctypes
import math
import os
import sys
from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from gridcap import PROGRAMS, Portfolio

CONTRACTOR_FEE = 300          # $k for one program's contractor in one year


@dataclass
class CrewModel:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]          # x[i, t] = 1: project i starts in year t
    hire: dict[tuple[str, int], mathopt.Variable]       # hire[g, y] = 1: program g hires a contractor in year y
    use: dict[tuple[str, int], mathopt.LinearExpression]
    big_m: dict[tuple[str, int], float]


def active(project, t: int, year: int) -> bool:
    """Is a project that starts in year t being worked on in `year`?"""
    return t <= year < t + project.duration


def crew_use(portfolio: Portfolio, x: dict) -> dict[tuple[str, int], mathopt.LinearExpression]:
    """Crew-months each program uses in each year: every active project needs its crew_months."""
    use = {(g, y): mathopt.LinearExpression() for g in PROGRAMS for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            for y in portfolio.years:
                if active(p, t, y):
                    use[p.program, y] += p.crew_months * x[p.project_id, t]
    return use


def m_from_variable_bounds(portfolio: Portfolio) -> dict[tuple[str, int], int]:
    """Every x at its upper bound 1: the largest the row's left side can be, less the crews in house."""
    m = {}
    for g in PROGRAMS:
        for y in portfolio.years:
            most = sum(p.crew_months for p in portfolio.projects if p.program == g
                       for t in p.starts() if active(p, t, y))
            m[g, y] = max(0, most - portfolio.crews[g, y])
    return m


def m_from_once_rows(portfolio: Portfolio) -> dict[tuple[str, int], int]:
    """A project starts at most once, so it adds its crew_months once, if any start reaches the year."""
    m = {}
    for g in PROGRAMS:
        for y in portfolio.years:
            most = sum(p.crew_months for p in portfolio.projects if p.program == g
                       and any(active(p, t, y) for t in p.starts()))
            m[g, y] = max(0, most - portfolio.crews[g, y])
    return m


def m_by_solving(portfolio: Portfolio, *, integer: bool) -> dict[tuple[str, int], int]:
    """The largest crew use the other rows allow, per row, found by maximizing it: an LP or the MILP."""
    m = {}
    for key, crews in portfolio.crews.items():
        cm = build(portfolio, 0, integer=integer, form="none")
        cm.model.maximize(cm.use[key])
        most = quiet_solve(cm.model, mathopt.SolverType.HIGHS if integer else mathopt.SolverType.GLOP,
                           params=mathopt.SolveParameters(relative_gap_tolerance=0.0) if integer else None)
        m[key] = max(0, math.floor(most.objective_value() + 1e-6) - crews)
    return m


def build(portfolio: Portfolio, big_m, *, integer: bool = True, form: str = "big_m",
          fee: int = CONTRACTOR_FEE) -> CrewModel:
    """The model. `big_m` is a dict per (program, year) or one number for every row.

    form="big_m" writes use <= crews + M * hire; form="indicator" writes "hire = 0 implies
    use <= crews" and needs a solver that takes indicator constraints (SCIP here, not HiGHS);
    form="none" leaves the crew rule out.
    """
    model = mathopt.Model(name=f"{portfolio.name} crews")
    x = {(p.project_id, t): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}
    hire = {(g, y): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"hire_{g}_{y}")
            for g in PROGRAMS for y in portfolio.years}
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
            parent = by_id[c.parent]
            for t in c.starts():
                model.add_linear_constraint(
                    sum(x[c.project_id, u] for u in c.starts() if u <= t)
                    <= sum(x[parent.project_id, s] for s in parent.starts() if s <= t - c.parent_lag),
                    name=f"after_{c.project_id}_{t}")
    for y in portfolio.years:
        spend = sum(p.spend(t)[y] * x[p.project_id, t] for p in portfolio.projects for t in p.starts()
                    if y in p.spend(t))
        model.add_linear_constraint(spend <= portfolio.budget[y], name=f"budget_{y}")

    use = crew_use(portfolio, x)
    big = big_m if isinstance(big_m, dict) else {key: big_m for key in hire}
    for (g, y), h in hire.items():
        crews = portfolio.crews[g, y]
        if form == "big_m":
            model.add_linear_constraint(use[g, y] <= crews + big[g, y] * h, name=f"crews_{g}_{y}")
        elif form == "indicator":
            model.add_indicator_constraint(indicator=h, activate_on_zero=True,
                                           implied_constraint=use[g, y] <= crews, name=f"crews_{g}_{y}")
        elif form == "none":
            pass
        else:
            raise ValueError(form)

    model.maximize(sum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts())
                   - fee * sum(hire.values()))
    return CrewModel(model, x, hire, use, big)


def hired(cm: CrewModel, result: mathopt.SolveResult) -> list[tuple[str, int]]:
    return [key for key, h in cm.hire.items() if result.variable_values(h) > 0.5]


def quiet_solve(model: mathopt.Model, solver: mathopt.SolverType = mathopt.SolverType.HIGHS,
                params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
    """Solve, keeping the bundled HiGHS's stray debug line out of the output.

    Standard output points at /dev/null during the solve, and the C buffer is flushed there before
    it is restored.
    """
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(model, solver, params=params)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)
