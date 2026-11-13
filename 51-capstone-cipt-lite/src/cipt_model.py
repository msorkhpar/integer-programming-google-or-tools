"""CIPT Lite, milestone 2: the multi-period selection model with every section 6 rule GridCap's data carries.

GridCap is a fictional utility's portfolio, generated for this course; none of its numbers are real.

`build(portfolio, scenario)` writes the model of lesson 13.1.2 in MathOpt. Every row has the name the
lesson's formulation gives it (`must_P017`, `after_P024_2029`, `crews_vegetation_2031`, ...), and
`rules` maps each name to its row, so milestone 4 can talk about rows by name. `check(...)` is the
rule checker: it reads only the data and a plan, never the model, so a wrong row cannot approve its
own plan (lesson 12.3.2).

`solve` runs HiGHS on one thread, with a zero gap by default and stray C output kept off the
program's output (docs/FINDINGS.md, F9). HiGHS fixes its thread count at the first solve of a process
(F26), so every solve of the capstone passes the same options.
"""

from __future__ import annotations

import contextlib
import ctypes
import os
import sys
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt
from ortools.math_opt.solvers import highs_pb2

from gridcap import Portfolio

#: One thread, set in HiGHS's own options (lesson 10.2.2); the gap is the run's setting.
HIGHS = highs_pb2.HighsOptionsProto(int_options={"threads": 1})


@dataclass(frozen=True)
class Scenario:
    """What planners and finance change before a run (lesson 12.1.1). Empty means GridCap's own data."""

    name: str = "base"
    budget: dict[int, int] = field(default_factory=dict)                  # year -> $k
    crews: dict[tuple[str, int], int] = field(default_factory=dict)       # (program, year) -> crew-months
    fix_start: dict[str, int] = field(default_factory=dict)               # project -> the year it must start
    force_in: frozenset[str] = frozenset()                                # fund in some year of its window
    force_out: frozenset[str] = frozenset()                               # never fund


@dataclass
class Built:
    portfolio: Portfolio
    scenario: Scenario
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]
    rules: dict[str, mathopt.LinearConstraint] = field(default_factory=dict)
    npv: mathopt.LinearExpression = field(default_factory=mathopt.LinearExpression)

    def started(self, pid: str) -> mathopt.LinearExpression:
        """s_i: 1 if project `pid` starts in some year, else 0."""
        return mathopt.LinearExpression() + mathopt.fast_sum(
            v for (p, _), v in self.x.items() if p == pid)

    def add(self, name: str, row) -> None:
        self.rules[name] = self.model.add_linear_constraint(row, name=name)


def budgets(portfolio: Portfolio, scenario: Scenario) -> dict[int, int]:
    return {y: scenario.budget.get(y, portfolio.budget[y]) for y in portfolio.years}


def crew_limits(portfolio: Portfolio, scenario: Scenario) -> dict[tuple[str, int], int]:
    return {k: scenario.crews.get(k, v) for k, v in portfolio.crews.items()}


def active(project, start: int, year: int) -> bool:
    """Is a project that starts in `start` being worked on in `year`?"""
    return start <= year < start + project.duration


def build(portfolio: Portfolio, scenario: Scenario = Scenario()) -> Built:
    model = mathopt.Model(name=f"{portfolio.name} {scenario.name}")
    x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}
    b = Built(portfolio, scenario, model, x)
    by_id = {p.project_id: p for p in portfolio.projects}

    # Overrides are bounds on the start variables (lesson 6.5.6); "fund it in any year" is a row.
    for pid, year in scenario.fix_start.items():
        for (p, t), v in x.items():
            if p == pid:
                v.lower_bound = v.upper_bound = 1.0 if t == year else 0.0
    for pid in scenario.force_out:
        for (p, t), v in x.items():
            if p == pid:
                v.upper_bound = 0.0

    for p in portfolio.projects:                                          # (once_i) and (must_i)
        if p.must_do:
            b.add(f"must_{p.project_id}", b.started(p.project_id) == 1)
        else:
            b.add(f"once_{p.project_id}", b.started(p.project_id) <= 1)
    for pid in sorted(scenario.force_in):                                 # (force_i)
        b.add(f"force_{pid}", b.started(pid) >= 1)

    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in sorted(groups.items()):                             # (alt_g)
        b.add(f"alt_{g}", mathopt.fast_sum(b.started(m) for m in members) <= 1)

    for c in portfolio.projects:                                          # (after_{c,t}), cumulative form
        if c.parent:
            parent = by_id[c.parent]
            for t in c.starts():
                b.add(f"after_{c.project_id}_{t}",
                      mathopt.LinearExpression()
                      + mathopt.fast_sum(x[c.project_id, u] for u in c.starts() if u <= t)
                      - mathopt.fast_sum(x[parent.project_id, s] for s in parent.starts()
                                         if s <= t - c.parent_lag) <= 0)

    spend = {y: mathopt.LinearExpression() for y in portfolio.years}
    region = {k: mathopt.LinearExpression() for k in portfolio.region_budget}
    crews = {k: mathopt.LinearExpression() for k in portfolio.crews}
    for p in portfolio.projects:
        for t in p.starts():
            v = x[p.project_id, t]
            for year, amount in p.spend(t).items():
                spend[year] += amount * v
                region[p.region, year] += amount * v
                crews[p.program, year] += p.crew_months * v
    for y, limit in budgets(portfolio, scenario).items():                 # (budget_y)
        b.add(f"budget_{y}", spend[y] <= limit)
    for (r, y), limit in sorted(portfolio.region_budget.items()):         # (region_{r,y})
        b.add(f"region_{r}_{y}", region[r, y] <= limit)
    for (g, y), limit in sorted(crew_limits(portfolio, scenario).items()):   # (crews_{g,y})
        b.add(f"crews_{g}_{y}", crews[g, y] <= limit)
    for r, floor in sorted(portfolio.region_floor.items()):              # (floor_r)
        b.add(f"floor_{r}", mathopt.fast_sum(p.capex * x[p.project_id, t] for p in portfolio.projects
                                             if p.region == r for t in p.starts()) >= floor)

    b.npv = mathopt.fast_sum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts())
    model.maximize(b.npv)
    return b


def plan_of(b: Built, result: mathopt.SolveResult) -> dict[str, int]:
    """Project id -> start year, for every start the result sets to 1 (read with a tolerance)."""
    values = result.variable_values()
    return {pid: t for (pid, t), v in sorted(b.x.items()) if values[v] > 0.5}


@contextlib.contextmanager
def quiet():
    """Keep the bundled HiGHS's stray C output off the program's output (docs/FINDINGS.md, F9)."""
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        yield
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


def params(gap: float = 0.0, **common) -> mathopt.SolveParameters:
    """HiGHS on one thread, with the given relative gap and any common parameter (node_limit, ...)."""
    return mathopt.SolveParameters(relative_gap_tolerance=gap, highs=HIGHS, **common)


def solve(model: mathopt.Model, solve_params: mathopt.SolveParameters | None = None,
          model_params: mathopt.ModelSolveParameters | None = None) -> mathopt.SolveResult:
    with quiet():
        return mathopt.solve(model, mathopt.SolverType.HIGHS, params=solve_params or params(),
                             model_params=model_params)


def check(portfolio: Portfolio, scenario: Scenario, plan: dict[str, int]) -> list[str]:
    """Every rule the plan breaks, by row name, computed from the data alone (no model, no solver)."""
    broken = []
    by_id = {p.project_id: p for p in portfolio.projects}
    for pid, t in plan.items():
        if t not in by_id[pid].starts():
            broken.append(f"window_{pid}")
    for p in portfolio.projects:
        if p.must_do and p.project_id not in plan:
            broken.append(f"must_{p.project_id}")
    for pid in sorted(scenario.force_in):
        if pid not in plan:
            broken.append(f"force_{pid}")
    for pid, year in sorted(scenario.fix_start.items()):
        if plan.get(pid) != year:
            broken.append(f"fix_{pid}")
    for pid in sorted(scenario.force_out):
        if pid in plan:
            broken.append(f"out_{pid}")
    groups: dict[str, int] = {}
    for pid in plan:
        if by_id[pid].alt_group:
            groups[by_id[pid].alt_group] = groups.get(by_id[pid].alt_group, 0) + 1
    broken += [f"alt_{g}" for g, n in sorted(groups.items()) if n > 1]
    for pid, t in sorted(plan.items()):
        c = by_id[pid]
        if c.parent and (c.parent not in plan or plan[c.parent] + c.parent_lag > t):
            broken.append(f"after_{pid}_{t}")
    spend = {y: 0 for y in portfolio.years}
    region = {k: 0 for k in portfolio.region_budget}
    crews = {k: 0 for k in portfolio.crews}
    funded = {r: 0 for r in portfolio.region_floor}
    for pid, t in plan.items():
        p = by_id[pid]
        funded[p.region] += p.capex
        for year, amount in p.spend(t).items():
            spend[year] += amount
            region[p.region, year] += amount
            crews[p.program, year] += p.crew_months
    broken += [f"budget_{y}" for y, limit in budgets(portfolio, scenario).items() if spend[y] > limit]
    broken += [f"region_{r}_{y}" for (r, y), limit in sorted(portfolio.region_budget.items())
               if region[r, y] > limit]
    broken += [f"crews_{g}_{y}" for (g, y), limit in sorted(crew_limits(portfolio, scenario).items())
               if crews[g, y] > limit]
    broken += [f"floor_{r}" for r, floor in sorted(portfolio.region_floor.items()) if funded[r] < floor]
    return broken


def npv_of(portfolio: Portfolio, plan: dict[str, int]) -> int:
    by_id = {p.project_id: p for p in portfolio.projects}
    return sum(by_id[pid].npv[t] for pid, t in plan.items())


def allows(b: Built, plan: dict[str, int]) -> bool:
    """Does the model accept this whole plan? Fix every start variable by its bounds and ask HiGHS
    (lesson 12.3.1). A start the model has no variable for is refused before any solve."""
    if any((pid, t) not in b.x for pid, t in plan.items()):
        return False
    saved = {v: (v.lower_bound, v.upper_bound) for v in b.x.values()}
    try:
        for (pid, t), v in b.x.items():
            value = 1.0 if plan.get(pid) == t else 0.0
            if not saved[v][0] <= value <= saved[v][1]:         # an override's bound refuses it
                return False
            v.lower_bound = v.upper_bound = value
        return solve(b.model).termination.reason == mathopt.TerminationReason.OPTIMAL
    finally:
        for v, (lo, hi) in saved.items():
            v.lower_bound, v.upper_bound = lo, hi


def family(name: str) -> str:
    return name.split("_")[0]
