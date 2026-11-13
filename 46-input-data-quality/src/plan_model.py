"""Lesson 12.2.1: the multi-period planning model, built from a validated Snapshot.

The model of section 6 (lessons 6.4.1-6.5.x) with start-year variables, budgets, crews, regional
floors, alternatives and parent precedence, written against the snapshot schema of lesson 12.2.1.
GridCap is a fictional utility.
"""

from __future__ import annotations

import ctypes
import os
import sys
from dataclasses import dataclass

from ortools.math_opt.python import mathopt

from snapshot import Snapshot


@dataclass
class PlanModel:
    model: mathopt.Model
    x: dict[tuple[str, int], mathopt.Variable]


def starts(p, years: tuple[int, ...]) -> list[int]:
    """T_i: the window's start years whose work ends inside the plan."""
    return [t for t in range(p.earliest_start, p.latest_start + 1) if t + len(p.cost_profile) - 1 <= years[-1]]


def build(snap: Snapshot) -> PlanModel:
    m = mathopt.Model(name=snap.name)
    years = snap.years
    by_id = {p.project_id: p for p in snap.projects}
    x = {(p.project_id, t): m.add_binary_variable(name=f"x_{p.project_id}_{t}")
         for p in snap.projects for t in starts(p, years)}
    chosen = {pid: [v for (i, _), v in x.items() if i == pid] for pid in by_id}

    m.maximize(mathopt.fast_sum(by_id[i].npv[t - by_id[i].earliest_start] * v for (i, t), v in x.items()))
    for pid, p in by_id.items():
        if p.must_do:
            m.add_linear_constraint(mathopt.fast_sum(chosen[pid]) == 1, name=f"must_{pid}")
        else:
            m.add_linear_constraint(mathopt.fast_sum(chosen[pid]) <= 1, name=f"once_{pid}")
    for g in sorted({p.alt_group for p in snap.projects if p.alt_group}):
        members = [v for p in snap.projects if p.alt_group == g for v in chosen[p.project_id]]
        m.add_linear_constraint(mathopt.fast_sum(members) <= 1, name=f"alt_{g}")
    for c in snap.projects:
        if c.parent:
            for t in starts(c, years):
                started = mathopt.fast_sum(x[c.project_id, u] for u in starts(c, years) if u <= t)
                parent = mathopt.fast_sum(x[c.parent, s] for s in starts(by_id[c.parent], years)
                                          if s <= t - c.parent_lag)
                m.add_linear_constraint(started <= parent, name=f"after_{c.project_id}_{t}")
    budget = {b.year: b.amount for b in snap.budget}
    crews = {(c.program, c.year): c.crew_months for c in snap.crews}
    for y in years:
        spend = mathopt.fast_sum(by_id[i].cost_profile[y - t] * v for (i, t), v in x.items()
                                 if 0 <= y - t < len(by_id[i].cost_profile))
        m.add_linear_constraint(spend <= budget[y], name=f"budget_{y}")
        for q in ("transmission", "distribution", "vegetation"):
            need = mathopt.fast_sum(by_id[i].crew_months * v for (i, t), v in x.items()
                                    if by_id[i].program == q and 0 <= y - t < len(by_id[i].cost_profile))
            m.add_linear_constraint(need <= crews[q, y], name=f"crews_{q}_{y}")
    for f in snap.region_floor:
        spent = mathopt.fast_sum(sum(by_id[i].cost_profile) * v for (i, t), v in x.items()
                                 if by_id[i].region == f.region)
        m.add_linear_constraint(spent >= f.amount, name=f"floor_{f.region}")
    return PlanModel(m, x)


def solve(pm: PlanModel) -> mathopt.SolveResult:
    """Solve with HiGHS to a proven optimum, keeping its stray debug line out of the output."""
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(pm.model, mathopt.SolverType.HIGHS,
                             params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


def outcome(snap: Snapshot) -> str:
    """The solver's verdict on a snapshot: OPTIMAL with the NPV, or the termination reason."""
    result = solve(build(snap))
    reason = result.termination.reason
    if reason == mathopt.TerminationReason.OPTIMAL:
        return f"OPTIMAL, NPV ${result.objective_value():,.0f}k"
    return reason.name


def plan(pm: PlanModel, result: mathopt.SolveResult) -> dict[str, int]:
    return {i: t for (i, t), v in pm.x.items() if result.variable_values(v) > 0.5}
