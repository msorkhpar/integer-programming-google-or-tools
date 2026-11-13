"""The GridCap plan that module 39 explains, with every row named so a report can talk about rules.

GridCap is a fictional utility's portfolio, generated for this course; none of its numbers are real.

`build` writes the timing model of module 26 (lessons 6.4.1 to 6.4.3): one binary x[i, t] per
project and allowed start year, a once or must-do row per project, one row per alternative group,
cumulative precedence rows, and a budget row per year with each project's cost spread over its
years of work. A `Scenario` adds what planners change before a run (lesson 7.1.3): a budget per
year, projects forced in (in any year, or in a given one) and projects forced out.

`slack` measures a row against a plan without asking the solver, so it works on a MILP, where
MathOpt returns no dual values (lesson 9.2.1).

`solve_highs` keeps the bundled HiGHS's stray debug line out of the program's output,
as lesson 6.4.1's `timing_model.solve_highs` does.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import math
import os
import sys
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from gridcap import Portfolio

#: The solver settings every run uses and records (section 10 explains each one).
SETTINGS = {"solver": "HIGHS", "relative_gap_tolerance": 0.0}
EXACT = mathopt.SolveParameters(relative_gap_tolerance=0.0)
TOL = 1e-6


@dataclass(frozen=True)
class Scenario:
    """What planners and finance change before a run. Empty means GridCap's own data."""

    name: str = "base"
    budget: dict[int, int] = field(default_factory=dict)            # year -> budget, $k
    force_in: dict[str, int | None] = field(default_factory=dict)   # project -> start year, or None: any year
    force_out: frozenset[str] = frozenset()

    def inputs(self, portfolio: Portfolio) -> dict:
        """Everything the model is built from, in a JSON-ready form."""
        return {"portfolio": portfolio.content_hash(),
                "budget": {str(y): self.budget.get(y, portfolio.budget[y]) for y in portfolio.years},
                "force_in": {p: self.force_in[p] for p in sorted(self.force_in)},
                "force_out": sorted(self.force_out),
                "settings": SETTINGS}

    def snapshot(self, portfolio: Portfolio) -> str:
        """sha256 of the canonical inputs (lesson 7.1.3): equal inputs, equal id."""
        text = json.dumps(self.inputs(portfolio), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


@dataclass
class Built:
    portfolio: Portfolio
    scenario: Scenario
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]
    rows: dict[str, mathopt.LinearConstraint]
    spend: dict[int, mathopt.LinearExpression]


@dataclass
class Run:
    built: Built
    status: str
    npv: float | None
    plan: dict[str, int]                      # project -> start year, funded projects only
    result: mathopt.SolveResult | None = None


def build(portfolio: Portfolio, scenario: Scenario = Scenario(), *, integer: bool = True) -> Built:
    model = mathopt.Model(name=f"{portfolio.name} {scenario.name}")
    x = {(p.project_id, t): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}
    rows: dict[str, mathopt.LinearConstraint] = {}
    by_id = {p.project_id: p for p in portfolio.projects}

    def started(pid: str) -> mathopt.LinearExpression:
        return sum(x[pid, t] for t in by_id[pid].starts())

    def by(pid: str, year: int) -> mathopt.LinearExpression:
        return mathopt.LinearExpression() + sum(x[pid, s] for s in by_id[pid].starts() if s <= year)

    def add(name: str, bounded) -> None:
        rows[name] = model.add_linear_constraint(bounded, name=name)

    for p in portfolio.projects:
        pid = p.project_id
        if pid in scenario.force_out:
            add(f"out_{pid}", started(pid) == 0)
        if p.must_do:
            add(f"must_{pid}", started(pid) == 1)
        elif pid in scenario.force_in:
            add(f"in_{pid}", started(pid) == 1)
        elif pid not in scenario.force_out:
            add(f"once_{pid}", started(pid) <= 1)
        year = scenario.force_in.get(pid)
        if year is not None:
            add(f"in_{pid}_{year}", x[pid, year] == 1)
    groups: dict[str, list[str]] = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        add(f"alt_{g}", sum(started(m) for m in members) <= 1)
    for c in portfolio.projects:
        if c.parent:
            for t in c.starts():
                add(f"after_{c.project_id}_{t}", by(c.project_id, t) <= by(c.parent, t - c.parent_lag))
    spend = {y: mathopt.LinearExpression() for y in portfolio.years}
    for p in portfolio.projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                spend[year] += amount * x[p.project_id, t]
    for y in portfolio.years:
        add(f"budget_{y}", spend[y] <= scenario.budget.get(y, portfolio.budget[y]))
    model.maximize(sum(p.npv[t] * x[p.project_id, t] for p in portfolio.projects for t in p.starts()))
    return Built(portfolio, scenario, model, x, rows, spend)


def solve_highs(model: mathopt.Model, params: mathopt.SolveParameters | None = None) -> mathopt.SolveResult:
    """Solve with HiGHS, with the process's stdout pointed at /dev/null for the solve."""
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


def solve(built: Built) -> Run:
    """Solve to a proven optimum (gap 0) and read the plan; an infeasible run has no plan."""
    result = solve_highs(built.model, EXACT)
    reason = result.termination.reason
    if reason not in (mathopt.TerminationReason.OPTIMAL, mathopt.TerminationReason.FEASIBLE):
        return Run(built, reason.name, None, {}, result)
    plan = {pid: t for (pid, t), v in built.x.items() if result.variable_values(v) > 0.5}
    return Run(built, reason.name, result.objective_value(), plan, result)


def plan_values(built: Built, plan: dict[str, int]) -> dict[mathopt.Variable, float]:
    """The 0/1 value of every start variable for a plan {project: start year}."""
    return {v: 1.0 if plan.get(pid) == t else 0.0 for (pid, t), v in built.x.items()}


def activity(row: mathopt.LinearConstraint, values: dict[mathopt.Variable, float]) -> float:
    """The row's left-hand side evaluated at the plan."""
    return sum(term.coefficient * values[term.variable] for term in row.terms())


def slack(row: mathopt.LinearConstraint, values: dict[mathopt.Variable, float]) -> float:
    """Room left before the row's nearest bound: >= 0 when the row holds, 0 when it binds."""
    a = activity(row, values)
    room = []
    if row.upper_bound < math.inf:
        room.append(row.upper_bound - a)
    if row.lower_bound > -math.inf:
        room.append(a - row.lower_bound)
    return min(room)


def family(name: str) -> str:
    """The rule family a row name belongs to: budget_2029 -> budget."""
    return name.split("_")[0]


def real_spend(portfolio: Portfolio, plan: dict[str, int]) -> dict[int, int]:
    """What a plan spends each year, summed from the cost profiles, not from the model."""
    spend = {y: 0 for y in portfolio.years}
    for pid, t in plan.items():
        for y, amount in portfolio.project(pid).spend(t).items():
            spend[y] += amount
    return spend
