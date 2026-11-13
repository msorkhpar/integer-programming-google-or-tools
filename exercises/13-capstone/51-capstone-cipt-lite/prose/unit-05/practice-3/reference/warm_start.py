"""Milestone 5: last cycle's plan as a warm start for this cycle's solve.

A practice portfolio is a dict in the milestones' shape, reduced here to years, budget and projects.
A plan is {project id: start year}. The data is invented for a fictional utility.
"""

from __future__ import annotations

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


def carry(last: dict[str, int], snapshot: dict) -> dict[str, int]:
    """Last cycle's starts that still have a variable; a child whose parent is not carried goes too."""
    jobs = snapshot["projects"]
    plan = {j: t for j, t in last.items() if j in jobs and t in starts(jobs[j])}
    while orphans := [j for j in plan if jobs[j]["parent"] and jobs[j]["parent"] not in plan]:
        for j in orphans:
            del plan[j]
    return plan


def repair(snapshot: dict, plan: dict[str, int]) -> dict[str, int]:
    """Drop optional projects until no budget row is broken, least NPV per $k first, among the projects
    that spend in a broken year; a dropped project's children (and theirs) go with it. Never a must-do,
    and never a project with a must-do among its descendants in the plan."""
    jobs, plan = snapshot["projects"], dict(plan)

    def needed(j: str) -> bool:
        """j is a must-do, or dropping it would take a must-do descendant with it."""
        return jobs[j]["must"] or any(needed(c) for c in plan if jobs[c]["parent"] == j)

    while broken := [int(r.split("_")[1]) for r in check(snapshot, plan) if r.startswith("budget_")]:
        optional = [j for j, t in plan.items() if not needed(j) and set(spend(jobs[j], t)) & set(broken)]
        if not optional:
            break
        out = [min(optional, key=lambda j: (jobs[j]["npv"][plan[j]] / sum(jobs[j]["cost"]), j))]
        while out:
            j = out.pop()
            plan.pop(j, None)
            out += [c for c in plan if jobs[c]["parent"] == j]
    return plan


def hint(x: dict, plan: dict[str, int]) -> mathopt.ModelSolveParameters:
    """A complete hint: every start variable set, 1 for the plan's starts and 0 for the rest."""
    values = {v: 1.0 if plan.get(j) == t else 0.0 for (j, t), v in x.items()}
    return mathopt.ModelSolveParameters(solution_hints=[mathopt.SolutionHint(variable_values=values)])


if __name__ == "__main__":
    snapshot = {"years": [2027, 2028], "budget": {2027: 100, 2028: 100},
                "projects": {"J1": {"cost": [80], "earliest": 2027, "latest": 2028, "must": False, "parent": None,
                                    "lag": 0, "group": None, "npv": {2027: 50, 2028: 45}}}}
    model, x = build(snapshot)
    start = repair(snapshot, carry({"J1": 2027, "J0": 2026}, snapshot))
    result = solve(model, hint(x, start))
    print(start, result.termination.reason.name, result.objective_value())
