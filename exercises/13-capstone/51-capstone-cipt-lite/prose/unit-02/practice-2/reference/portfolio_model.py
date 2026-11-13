from __future__ import annotations

import contextlib
import ctypes
import os
import sys

from ortools.math_opt.python import mathopt

Plan = dict[str, int]


# --- Given: the variables, a quiet solve, the plan reader, and the plan test ----------------------

def variables(model: mathopt.Model, snap: dict) -> dict[tuple[str, int], mathopt.Variable]:
    """x[j, t] in {0, 1} for every project j and every start year t of its window."""
    return {(j, t): model.add_binary_variable(name=f"x_{j}_{t}")
            for j, p in snap["projects"].items() for t in range(p["earliest"], p["latest"] + 1)}


@contextlib.contextmanager
def quiet():
    """Keep the HiGHS bundled with OR-Tools from printing a stray line on some solves."""
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


def solve(model: mathopt.Model) -> mathopt.SolveResult:
    with quiet():
        return mathopt.solve(model, mathopt.SolverType.HIGHS,
                             params=mathopt.SolveParameters(relative_gap_tolerance=0.0))


def build(snap: dict) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="practice portfolio")
    x = variables(model, snap)
    add_rules(model, x, snap)
    set_objective(model, x, snap)
    return model, x


def best(snap: dict) -> tuple[float, Plan]:
    """The optimal plan's objective value and the plan, {project: start year}."""
    model, x = build(snap)
    result = solve(model)
    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL, result.termination
    values = result.variable_values()
    return result.objective_value(), {j: t for (j, t), v in sorted(x.items()) if values[v] > 0.5}


def allows(snap: dict, plan: Plan) -> bool:
    """Does the model accept this whole plan? Every start variable is fixed by its bounds."""
    model, x = build(snap)
    if any((j, t) not in x for j, t in plan.items()):
        return False                                   # a start the model has no variable for
    for (j, t), v in x.items():
        v.lower_bound = v.upper_bound = 1.0 if plan.get(j) == t else 0.0
    return solve(model).termination.reason == mathopt.TerminationReason.OPTIMAL


# --- Yours: every rule, and the objective -------------------------------------------------------

def add_rules(model: mathopt.Model, x: dict, snap: dict) -> None:
    projects, years = snap["projects"], snap["years"]

    def starts(j: str) -> list[int]:
        return [t for (i, t) in x if i == j]

    def funded(j: str) -> mathopt.LinearExpression:
        return mathopt.LinearExpression() + sum(x[j, t] for t in starts(j))

    for j, p in projects.items():
        if p["must"]:
            model.add_linear_constraint(funded(j) == 1, name=f"must_{j}")
        else:
            model.add_linear_constraint(funded(j) <= 1, name=f"once_{j}")

    groups: dict[str, list[str]] = {}
    for j, p in projects.items():
        if p["group"] is not None:
            groups.setdefault(p["group"], []).append(j)
    for g, members in groups.items():
        model.add_linear_constraint(sum(funded(j) for j in members) <= 1, name=f"alt_{g}")

    for j, p in projects.items():
        if p["parent"] is None:
            continue
        mother = p["parent"]
        for t in starts(j):
            started_child = mathopt.LinearExpression() + sum(x[j, u] for u in starts(j) if u <= t)
            started_parent = sum(x[mother, s] for s in starts(mother) if s + p["lag"] <= t)
            model.add_linear_constraint(started_child - started_parent <= 0, name=f"after_{j}_{t}")

    def at_work(j: str, y: int):
        """(start variable, year of work k) for each start of j that has j working in year y."""
        return [(x[j, t], y - t) for t in starts(j) if 0 <= y - t < len(projects[j]["cost"])]

    for y in years:
        money = mathopt.LinearExpression() + sum(projects[j]["cost"][k] * v for j in projects
                                                 for v, k in at_work(j, y))
        model.add_linear_constraint(money <= snap["budget"][y], name=f"budget_{y}")
        for region, limits in snap["region_budget"].items():
            mine = mathopt.LinearExpression() + sum(projects[j]["cost"][k] * v for j in projects
                                                    if projects[j]["region"] == region for v, k in at_work(j, y))
            model.add_linear_constraint(mine <= limits[y], name=f"region_{region}_{y}")
        for program, limits in snap["crews"].items():
            busy = mathopt.LinearExpression() + sum(projects[j]["crews"] * v for j in projects
                                                    if projects[j]["program"] == program for v, _ in at_work(j, y))
            model.add_linear_constraint(busy <= limits[y], name=f"crews_{program}_{y}")

    for region, floor in snap["floor"].items():
        capex = mathopt.LinearExpression() + sum(sum(projects[j]["cost"]) * funded(j) for j in projects
                                                 if projects[j]["region"] == region)
        model.add_linear_constraint(capex >= floor, name=f"floor_{region}")


def set_objective(model: mathopt.Model, x: dict, snap: dict) -> None:
    model.maximize(mathopt.LinearExpression() + sum(snap["projects"][j]["npv"][t] * v for (j, t), v in x.items()))


if __name__ == "__main__":
    snap = {"years": [2027, 2028], "rate": 0.05, "budget": {2027: 100, 2028: 100},
            "region_budget": {"North": {2027: 100, 2028: 100}}, "crews": {"lines": {2027: 1, 2028: 1}},
            "floor": {"North": 0},
            "projects": {"J1": {"program": "lines", "region": "North", "cost": [80], "earliest": 2027,
                                "latest": 2028, "must": True, "parent": None, "lag": 0, "group": None,
                                "crews": 1, "npv": {2027: 30, 2028: 25}}}}
    print(best(snap))
