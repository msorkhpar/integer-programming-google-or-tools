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
    """Every row of your formulation, each named as the table in the statement says."""
    # TODO: once/must, alt, after (with the lag), budget, region, crews, floor.


def set_objective(model: mathopt.Model, x: dict, snap: dict) -> None:
    """Maximize the plan's NPV, each start at its own start year's value."""
    # TODO
    model.maximize(mathopt.LinearExpression())


if __name__ == "__main__":
    snap = {"years": [2027, 2028], "rate": 0.05, "budget": {2027: 100, 2028: 100},
            "region_budget": {"North": {2027: 100, 2028: 100}}, "crews": {"lines": {2027: 1, 2028: 1}},
            "floor": {"North": 0},
            "projects": {"J1": {"program": "lines", "region": "North", "cost": [80], "earliest": 2027,
                                "latest": 2028, "must": True, "parent": None, "lag": 0, "group": None,
                                "crews": 1, "npv": {2027: 30, 2028: 25}}}}
    print(best(snap))
