"""The GridCap plan every program of module 37 diagnoses, and the Budget Lock scenario that breaks it.

GridCap is a fictional utility's portfolio; none of its numbers are real. `build` writes the timing
model of lesson 6.4.1 (start-year binaries, once and must-do rows, alternatives, cumulative
precedence, yearly budgets) plus three rule families that planners touch at Budget Lock (lesson
7.1.3): crew-months per program and year, each region's floor over the plan, and the planners'
overrides that force a project in (in a given year) or out. Every row has a name, and `rules`
maps each name to its row, so a diagnosis can talk about rows by name.

`LOCK` is the scenario this module explains: finance locks 2028 at $6,000k, a contractor change
leaves 12 transmission crew-months in each of 2030 and 2031, and the board forces P032 into 2028
and P023 into the plan.

`quiet`, `solve` and `refusal` are the helpers of lesson 4.3.5, repeated here so that this module
stands alone: stray C output that the HiGHS bundled with OR-Tools 9.15 prints on some MIP solves
kept off the program's output, and the reason OR-Tools 9.15 hides behind an AttributeError.
"""

from __future__ import annotations

import contextlib
import ctypes
import os
import sys
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from gridcap import Portfolio

EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)


@dataclass(frozen=True)
class Scenario:
    """What planners and finance change before a run. Empty means GridCap's own data."""

    name: str = "base"
    budget: dict[int, int] = field(default_factory=dict)                 # year -> locked budget, $k
    crews: dict[tuple[str, int], int] = field(default_factory=dict)      # (program, year) -> crew-months
    force_in: dict[str, int | None] = field(default_factory=dict)        # project -> start year, or None: any year
    force_out: frozenset[str] = frozenset()


LOCK = Scenario(
    name="budget-lock",
    budget={2028: 6000},
    crews={("transmission", 2030): 12, ("transmission", 2031): 12},
    force_in={"P032": 2028, "P023": None},
)


@dataclass
class LockModel:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]              # x[i, t] = 1: project i starts in year t
    rules: dict[str, mathopt.LinearConstraint] = field(default_factory=dict)   # row name -> row
    spend: dict[int, mathopt.LinearExpression] = field(default_factory=dict)
    npv: mathopt.LinearExpression = field(default_factory=mathopt.LinearExpression)

    def started(self, pid: str) -> mathopt.LinearExpression:
        """1 if project `pid` starts in any year, else 0."""
        return mathopt.fast_sum(v for (p, _), v in self.x.items() if p == pid)

    def add(self, name: str, row) -> None:
        self.rules[name] = self.model.add_linear_constraint(row, name=name)


def active(project, t: int, year: int) -> bool:
    """Is a project that starts in year t being worked on in `year`?"""
    return t <= year < t + project.duration


def build(portfolio: Portfolio, scenario: Scenario = Scenario(), *, integer: bool = True) -> LockModel:
    model = mathopt.Model(name=f"{portfolio.name} {scenario.name}")
    x = {(p.project_id, t): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}
    lm = LockModel(model, x)
    by_id = {p.project_id: p for p in portfolio.projects}
    for p in portfolio.projects:
        if p.must_do:
            lm.add(f"must_{p.project_id}", lm.started(p.project_id) == 1)
        else:
            lm.add(f"once_{p.project_id}", lm.started(p.project_id) <= 1)
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in sorted(groups.items()):
        lm.add(f"alt_{g}", mathopt.fast_sum(lm.started(m) for m in members) <= 1)
    for c in portfolio.projects:
        if c.parent:
            parent = by_id[c.parent]
            for t in c.starts():
                lm.add(f"after_{c.project_id}_{t}",
                       mathopt.fast_sum(x[c.project_id, u] for u in c.starts() if u <= t)
                       - mathopt.fast_sum(x[parent.project_id, s] for s in parent.starts() if s <= t - c.parent_lag)
                       <= 0)
    lm.spend = {y: mathopt.LinearExpression() for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                if year in lm.spend:
                    lm.spend[year] += amount * x[p.project_id, t]
    for y in portfolio.years:
        lm.add(f"budget_{y}", lm.spend[y] <= scenario.budget.get(y, portfolio.budget[y]))
    for (g, y), months in sorted(portfolio.crews.items()):
        use = [p.crew_months * x[p.project_id, t] for p in portfolio.projects if p.program == g
               for t in p.starts() if active(p, t, y)]
        if use:
            lm.add(f"crews_{g}_{y}", mathopt.fast_sum(use) <= scenario.crews.get((g, y), months))
    for r, floor in sorted(portfolio.region_floor.items()):
        lm.add(f"floor_{r}", mathopt.fast_sum(p.capex * x[p.project_id, t] for p in portfolio.projects
                                              if p.region == r for t in p.starts()) >= floor)
    for pid, year in sorted(scenario.force_in.items()):
        if year is None:
            lm.add(f"force_{pid}", lm.started(pid) >= 1)
        else:
            lm.add(f"force_{pid}_{year}", x[pid, year] >= 1)
    for pid in sorted(scenario.force_out):
        lm.add(f"drop_{pid}", lm.started(pid) <= 0)
    lm.npv = mathopt.fast_sum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts())
    model.maximize(lm.npv)
    return lm


def plan(lm: LockModel, result: mathopt.SolveResult) -> dict[str, int]:
    """Project id -> start year, for every project the result starts."""
    values = result.variable_values()
    return {pid: t for (pid, t), v in lm.x.items() if values[v] > 0.5}


def refusal(error: BaseException) -> str:
    """The solver's own reason for an error: OR-Tools 9.15 raises an AttributeError whose
    `__context__` holds the real message (lesson 4.2.4). Falls back to the error itself."""
    inner = error.__context__ or error.__cause__
    return str(inner if inner is not None else error)


@contextlib.contextmanager
def quiet():
    """Point standard output and error at /dev/null while a solver runs, then flush the C buffers there.

    The HiGHS bundled with OR-Tools 9.15 prints a stray debug line on some MIP solves, and
    GLOP writes absl warnings to standard error; programs that want a log use `msg_cb` instead.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    saved = os.dup(1), os.dup(2)
    sink = os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    os.dup2(sink, 2)
    try:
        yield
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved[0], 1)
        os.dup2(saved[1], 2)
        for fd in (*saved, sink):
            os.close(fd)


def solve(model: mathopt.Model, solver: mathopt.SolverType = mathopt.SolverType.HIGHS, **kwargs) -> mathopt.SolveResult:
    """`mathopt.solve` with stray output suppressed; every keyword argument passes through."""
    kwargs.setdefault("params", EXACT)
    with quiet():
        return mathopt.solve(model, solver, **kwargs)
