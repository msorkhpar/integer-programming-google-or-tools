"""Milestone 5: properties every plan must keep, checked on practice portfolios drawn around a witness.

A practice portfolio is a dict in the milestones' shape, reduced here to years, budget and projects:
    {"years": [...], "budget": {year: $k}, "projects": {id: {"cost": [...], "earliest", "latest",
     "must", "parent", "lag", "group", "npv": {start year: $k}}}}
A plan is {project id: start year}. The portfolios are invented test data for a fictional utility.
"""

from __future__ import annotations

from hypothesis import strategies as st

# ---- given: milestone 2's model and rule checker, with a reduced rule set ----------------------------

import contextlib
import ctypes
import os
import sys

from ortools.math_opt.python import mathopt


def starts(job: dict) -> range:
    return range(job["earliest"], job["latest"] + 1)


def spend(job: dict, start: int) -> dict[int, int]:
    """What a project started in `start` spends in each year of work."""
    return {start + k: c for k, c in enumerate(job["cost"])}


def build(snapshot: dict, skip: frozenset = frozenset()):
    """Milestone 2's model, with must_, once_, alt_, after_ and budget_ rows only.

    `skip` plants a bug, for testing the tests: "must", "alt" or "budget" leaves those rows out,
    "lag" reads every lag as 0, "value" adds a stray 1 to the objective.
    """
    jobs = snapshot["projects"]
    model = mathopt.Model(name="practice plan")
    x = {(j, t): model.add_binary_variable(name=f"x_{j}_{t}") for j in sorted(jobs) for t in starts(jobs[j])}

    def started(j):
        return mathopt.LinearExpression() + mathopt.fast_sum(x[j, t] for t in starts(jobs[j]))

    for j in sorted(jobs):
        if jobs[j]["must"] and "must" not in skip:
            model.add_linear_constraint(started(j) == 1, name=f"must_{j}")
        else:
            model.add_linear_constraint(started(j) <= 1, name=f"once_{j}")
    groups: dict[str, list[str]] = {}
    for j in sorted(jobs):
        if jobs[j]["group"]:
            groups.setdefault(jobs[j]["group"], []).append(j)
    for g, members in sorted(groups.items()):
        if "alt" not in skip:
            model.add_linear_constraint(mathopt.fast_sum(started(m) for m in members) <= 1, name=f"alt_{g}")
    for c in sorted(jobs):
        p, lag = jobs[c]["parent"], 0 if "lag" in skip else jobs[c]["lag"]
        if p:
            for t in starts(jobs[c]):
                model.add_linear_constraint(
                    mathopt.LinearExpression() + mathopt.fast_sum(x[c, u] for u in starts(jobs[c]) if u <= t)
                    - mathopt.fast_sum(x[p, s] for s in starts(jobs[p]) if s <= t - lag) <= 0, name=f"after_{c}_{t}")
    for y in snapshot["years"]:
        if "budget" not in skip:
            model.add_linear_constraint(
                mathopt.LinearExpression() + mathopt.fast_sum(
                    spend(jobs[j], t).get(y, 0) * v for (j, t), v in x.items()) <= snapshot["budget"][y],
                name=f"budget_{y}")
    model.maximize(mathopt.fast_sum(jobs[j]["npv"][t] * v for (j, t), v in x.items()) + (1 if "value" in skip else 0))
    return model, x


@contextlib.contextmanager
def _quiet():
    """Keep the bundled HiGHS's stray C output off the screen."""
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


def solve(model, model_params=None) -> mathopt.SolveResult:
    """HiGHS to a zero gap."""
    with _quiet():
        return mathopt.solve(model, mathopt.SolverType.HIGHS,
                             params=mathopt.SolveParameters(relative_gap_tolerance=0.0), model_params=model_params)


def plan_of(x, result) -> dict[str, int]:
    values = result.variable_values()
    return {j: t for (j, t), v in x.items() if values[v] > 0.5}


def value(snapshot: dict, plan: dict[str, int]) -> int:
    return sum(snapshot["projects"][j]["npv"][t] for j, t in plan.items())


def check(snapshot: dict, plan: dict[str, int]) -> list[str]:
    """Every rule the plan breaks, by row name, from the data alone."""
    jobs, broken = snapshot["projects"], []
    broken += [f"window_{j}" for j, t in sorted(plan.items()) if t not in starts(jobs[j])]
    broken += [f"must_{j}" for j in sorted(jobs) if jobs[j]["must"] and j not in plan]
    groups: dict[str, int] = {}
    for j in plan:
        if jobs[j]["group"]:
            groups[jobs[j]["group"]] = groups.get(jobs[j]["group"], 0) + 1
    broken += [f"alt_{g}" for g, n in sorted(groups.items()) if n > 1]
    for c, t in sorted(plan.items()):
        p = jobs[c]["parent"]
        if p and (p not in plan or plan[p] + jobs[c]["lag"] > t):
            broken.append(f"after_{c}_{t}")
    for y in snapshot["years"]:
        if sum(spend(jobs[j], t).get(y, 0) for j, t in plan.items()) > snapshot["budget"][y]:
            broken.append(f"budget_{y}")
    return broken


# ---- yours -----------------------------------------------------------------------------------------

YEARS = [2027, 2028, 2029]


@st.composite
def portfolios(draw, max_projects: int = 6):
    """(snapshot, witness): a drawn portfolio and a plan that breaks none of its rules."""
    # TODO: draw the projects and a witness plan first, then budgets around the witness.
    return {"years": YEARS, "budget": {y: 0 for y in YEARS}, "projects": {}}, {}


def holds(snapshot: dict, witness: dict[str, int], skip: frozenset = frozenset()) -> None:
    """Solve `build(snapshot, skip)` and fail an assert if any property does not hold."""
    # TODO


if __name__ == "__main__":
    example = {"years": YEARS, "budget": {2027: 100, 2028: 100, 2029: 100},
               "projects": {"J1": {"cost": [80], "earliest": 2027, "latest": 2028, "must": True, "parent": None,
                                   "lag": 0, "group": None, "npv": {2027: 50, 2028: 45}}}}
    holds(example, {"J1": 2027})
    print("every property holds on the example")
