"""Milestone 6: an endpoint that returns the NPV against risk-removed frontier of a practice portfolio.

Each project carries, beside "npv", a "risk" table: the risk it removes ($k) for each start year,
milestone 3's coefficients. The practice portfolio is invented for a fictional utility.
"""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, ConfigDict, Field

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


def objectives(snapshot: dict, x: dict):
    """The two objective expressions: NPV and risk removed, both in $k."""
    jobs = snapshot["projects"]
    npv = mathopt.fast_sum(jobs[j]["npv"][t] * v for (j, t), v in x.items())
    risk = mathopt.fast_sum(jobs[j]["risk"][t] * v for (j, t), v in x.items())
    return npv, risk


def score(snapshot: dict, plan: dict[str, int]) -> dict:
    jobs = snapshot["projects"]
    return {"npv": sum(jobs[j]["npv"][t] for j, t in plan.items()),
            "risk": sum(jobs[j]["risk"][t] for j, t in plan.items()), "plan": dict(sorted(plan.items()))}


def from_json(snapshot: dict) -> dict:
    """A snapshot sent as JSON, with its year keys made integers again."""
    out = {**snapshot, "budget": {int(y): b for y, b in snapshot["budget"].items()}}
    out["projects"] = {j: {**p, "npv": {int(t): v for t, v in p["npv"].items()},
                           "risk": {int(t): v for t, v in p["risk"].items()}}
                       for j, p in snapshot["projects"].items()}
    return out


class FrontierRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    snapshot: dict
    points: int = Field(default=5, ge=2, le=11)


# ---- yours -----------------------------------------------------------------------------------------


HOLD = 1e-6     # how far below its optimum the first objective may fall in the second solve, $k


def best(snapshot: dict, first: str, then: str, floors: dict[str, float]) -> dict | None:
    """Maximize `first`, then `then` with `first` held at its optimum; every floor holds. None if no plan."""
    model, x = build(snapshot)
    value = dict(zip(("npv", "risk"), objectives(snapshot, x)))
    for name, floor in floors.items():
        model.add_linear_constraint(value[name] >= floor)
    model.maximize(value[first])
    result = solve(model)
    if not result.has_primal_feasible_solution():
        return None
    model.add_linear_constraint(value[first] >= result.objective_value() - HOLD)
    model.maximize(value[then])
    return score(snapshot, plan_of(x, solve(model)))


def frontier(snapshot: dict, points: int) -> list[dict]:
    """The epsilon-constraint frontier: the two ends, then NPV maximized at evenly spaced risk floors."""
    top_npv = best(snapshot, "npv", "risk", {})
    top_risk = best(snapshot, "risk", "npv", {})
    found = []
    for k in range(points):
        floor = top_npv["risk"] + (top_risk["risk"] - top_npv["risk"]) * k / (points - 1)
        point = best(snapshot, "npv", "risk", {"risk": floor})
        if point is not None and all((q["npv"], q["risk"]) != (point["npv"], point["risk"]) for q in found):
            found.append(point)
    kept = [p for p in found if not any(q["npv"] >= p["npv"] and q["risk"] >= p["risk"] and q != p for q in found)]
    return sorted(kept, key=lambda p: p["risk"])


def create_app() -> FastAPI:
    app = FastAPI(title="Practice frontier")

    @app.post("/frontier")
    def pareto(request: FrontierRequest) -> dict:
        return {"objectives": ["npv", "risk"], "points": frontier(from_json(request.snapshot), request.points)}

    return app


if __name__ == "__main__":
    snapshot = {"years": [2027], "budget": {2027: 100}, "projects": {
        "J1": {"cost": [100], "earliest": 2027, "latest": 2027, "must": False, "parent": None, "lag": 0,
               "group": None, "npv": {2027: 50}, "risk": {2027: 10}},
        "J2": {"cost": [100], "earliest": 2027, "latest": 2027, "must": False, "parent": None, "lag": 0,
               "group": None, "npv": {2027: 20}, "risk": {2027: 40}}}}
    print(frontier(snapshot, 3))
