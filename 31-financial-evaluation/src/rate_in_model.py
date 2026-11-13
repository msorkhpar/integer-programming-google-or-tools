"""Solve lesson 6.4.2's multi-period model on GridCap small with the rebuilt NPV table, at two rates.

The rows are module 26's (once, must, alt, cumulative after, budget). Only the objective's
coefficients change between the two solves.
"""

import ctypes
import os
import sys

from ortools.math_opt.python import mathopt

from coefficients import coefficient_table
from gridcap_assumptions import benefit_assumptions


def solve_quietly(model: mathopt.Model) -> mathopt.SolveResult:
    """HiGHS in OR-Tools 9.15 can print a stray debug line on a MIP solve."""
    sys.stdout.flush()
    saved, sink = os.dup(1), os.open(os.devnull, os.O_WRONLY)
    os.dup2(sink, 1)
    try:
        return mathopt.solve(model, mathopt.SolverType.HIGHS,
                             params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    finally:
        ctypes.CDLL(None).fflush(None)
        os.dup2(saved, 1)
        os.close(saved)
        os.close(sink)


def plan(portfolio, npv: dict[tuple[str, int], int]) -> tuple[float, dict[str, int]]:
    model = mathopt.Model(name="timing")
    x = {(p.project_id, t): model.add_binary_variable(name=f"x_{p.project_id}_{t}")
         for p in portfolio.projects for t in p.starts()}
    by_id = {p.project_id: p for p in portfolio.projects}

    def started(pid, by=None):
        return sum(x[pid, t] for t in by_id[pid].starts() if by is None or t <= by)

    for p in portfolio.projects:
        if p.must_do:
            model.add_linear_constraint(started(p.project_id) == 1, name=f"must_{p.project_id}")
        else:
            model.add_linear_constraint(started(p.project_id) <= 1, name=f"once_{p.project_id}")
    groups = {}
    for p in portfolio.projects:
        if p.alt_group:
            groups.setdefault(p.alt_group, []).append(p.project_id)
    for g, members in groups.items():
        model.add_linear_constraint(sum(started(m) for m in members) <= 1, name=f"alt_{g}")
    for c in portfolio.projects:
        if c.parent:
            for t in c.starts():
                model.add_linear_constraint(started(c.project_id, t) <= started(c.parent, t - c.parent_lag),
                                            name=f"after_{c.project_id}_{t}")
    for y in portfolio.years:
        spend = sum(c * x[p.project_id, y - k] for p in portfolio.projects
                    for k, c in enumerate(p.cost_profile) if (p.project_id, y - k) in x)
        model.add_linear_constraint(spend <= portfolio.budget[y], name=f"budget_{y}")
    model.maximize(sum(npv[key] * var for key, var in x.items()))
    result = solve_quietly(model)
    return result.objective_value(), {pid: t for (pid, t), v in x.items() if result.variable_values(v) > 0.5}


small, assumptions = benefit_assumptions("small")
starts = {}
for rate in (0.03, 0.07, 0.12):
    table = coefficient_table(small, assumptions, rate)
    value, starts[rate] = plan(small, table)
    late = sum(1 for pid, t in starts[rate].items() if t > small.project(pid).earliest_start)
    print(f"rate {rate:>2.0%}: NPV ${value:,.0f}k, started {len(starts[rate])} of 40, {late} later than earliest")
for rate in (0.03, 0.12):
    moved = sorted(pid for pid in set(starts[0.07]) | set(starts[rate])
                   if starts[0.07].get(pid) != starts[rate].get(pid))
    print(f"starts that differ from the 7% plan at {rate:.0%}: {len(moved)}")
    for pid in moved:
        print(f"  {pid}: at 7% {starts[0.07].get(pid, '-')}, at {rate:.0%} {starts[rate].get(pid, '-')}")

def floor_slack(portfolio, starts: dict[str, int]) -> dict[str, int]:
    """Each region's funded capex less its floor (lesson 7.1.3's floor rows, left out of the model)."""
    return {r: sum(portfolio.project(pid).capex for pid in starts if portfolio.project(pid).region == r) - floor
            for r, floor in portfolio.region_floor.items()}


slack = floor_slack(small, starts[0.07])
print("7% plan, capex funded above each region floor ($k): "
      + ", ".join(f"{r} {v:,}" for r, v in slack.items()) + f"; every floor met: {min(slack.values()) >= 0}")
