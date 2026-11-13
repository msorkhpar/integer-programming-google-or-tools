"""The GridCap planning model that module 30's planning cycle optimizes, and the scenarios it runs on.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.

The model is the multi-period model of modules 26 and 27 (one binary x[i, t] per project and
allowed start year, spend spread over each project's years of work, a budget row per year), with
the rate-case floors of lesson 6.5.5 and the planner overrides of lesson 6.5.6. A `Scenario` holds
everything a run depends on, so the same scenario always builds the same model.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import sys
from dataclasses import dataclass, field

from ortools.math_opt.python import mathopt

from gridcap import REGIONS, Portfolio

#: The solver settings every run records with its inputs (section 10 explains each one).
SETTINGS = {"solver": "HIGHS", "relative_gap_tolerance": 0.0}


@dataclass
class Scenario:
    """A named set of planning inputs: budgets, floors and overrides on top of one portfolio."""

    name: str
    portfolio: Portfolio
    budget: dict[int, int]
    floor: dict[str, int]
    force_in: set[str] = field(default_factory=set)
    force_out: set[str] = field(default_factory=set)
    parent: str | None = None

    def inputs(self) -> dict:
        """Everything the model is built from, in a JSON-ready form."""
        return {"portfolio": self.portfolio.content_hash(),
                "budget": {str(y): v for y, v in sorted(self.budget.items())},
                "floor": dict(sorted(self.floor.items())),
                "force_in": sorted(self.force_in), "force_out": sorted(self.force_out),
                "settings": SETTINGS}

    def snapshot(self) -> str:
        """sha256 of the canonical inputs: equal inputs give the same id, any change gives another."""
        text = json.dumps(self.inputs(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


def base_scenario(portfolio: Portfolio, name: str = "base") -> Scenario:
    return Scenario(name, portfolio, dict(portfolio.budget), dict(portfolio.region_floor))


@dataclass
class Plan:
    scenario: Scenario
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]

    def started(self, pid: str) -> mathopt.LinearExpression:
        p = self.scenario.portfolio.project(pid)
        return mathopt.LinearExpression(sum(self.x[pid, t] for t in p.starts()))

    def started_by(self, pid: str, year: int) -> mathopt.LinearExpression:
        p = self.scenario.portfolio.project(pid)
        return mathopt.LinearExpression(sum(self.x[pid, t] for t in p.starts() if t <= year))


def build(s: Scenario) -> Plan:
    """The planning model of a scenario. Row names match the labels of lesson 7.1.3's model."""
    pf = s.portfolio
    model = mathopt.Model(name=f"{pf.name} {s.name}")
    x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
         for p in pf.projects for t in p.starts()}
    plan = Plan(s, model, x)
    for p in pf.projects:
        i = p.project_id
        if i in s.force_out:
            model.add_linear_constraint(plan.started(i) == 0, name=f"out_{i}")
        elif p.must_do or i in s.force_in:
            model.add_linear_constraint(plan.started(i) == 1, name=f"{'must' if p.must_do else 'in'}_{i}")
        else:
            model.add_linear_constraint(plan.started(i) <= 1, name=f"once_{i}")
    groups: dict[str, list[str]] = {}
    for p in pf.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        model.add_linear_constraint(sum(plan.started(m) for m in members) <= 1, name=f"alt_{g}")
    for c in pf.projects:
        if c.parent:
            for t in c.starts():
                model.add_linear_constraint(
                    plan.started_by(c.project_id, t) <= plan.started_by(c.parent, t - c.parent_lag),
                    name=f"after_{c.project_id}_{t}")
    spend = {y: mathopt.LinearExpression() for y in pf.years}
    for p in pf.projects:
        for t in p.starts():
            for year, amount in p.spend(t).items():
                spend[year] += amount * x[p.project_id, t]
    for y in pf.years:
        model.add_linear_constraint(spend[y] <= s.budget[y], name=f"budget_{y}")
    for r in REGIONS:
        received = sum(p.capex * plan.started(p.project_id) for p in pf.projects if p.region == r)
        model.add_linear_constraint(received >= s.floor[r], name=f"floor_{r}")
    model.maximize(sum(p.npv[t] * x[p.project_id, t] for p in pf.projects for t in p.starts()))
    return plan


def solve_highs(model: mathopt.Model) -> mathopt.SolveResult:
    """Solve with HiGHS, keeping the engine's stray debug line out of the output."""
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        params = mathopt.SolveParameters(relative_gap_tolerance=SETTINGS["relative_gap_tolerance"])
        return mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


@dataclass
class Run:
    """What one optimization of a scenario produced."""

    status: str
    npv: float | None
    starts: dict[str, int]
    snapshot: str


def optimize(s: Scenario) -> Run:
    plan = build(s)
    result = solve_highs(plan.model)
    status = result.termination.reason.name
    if status != "OPTIMAL":
        return Run(status, None, {}, s.snapshot())
    starts = {pid: t for (pid, t), v in plan.x.items() if result.variable_values(v) > 0.5}
    return Run(status, result.objective_value(), dict(sorted(starts.items())), s.snapshot())


def spend_of(portfolio: Portfolio, starts: dict[str, int]) -> dict[int, int]:
    """What a plan spends in each year of the horizon."""
    spend = {y: 0 for y in portfolio.years}
    for pid, t in starts.items():
        for year, amount in portfolio.project(pid).spend(t).items():
            spend[year] += amount
    return spend


def money(value: float) -> str:
    return f"${value:,.0f}k"
