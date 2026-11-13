import re

import pytest
from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

from determinism import assert_deterministic

# Four robots, five pipe segments; value of each robot on each segment; one robot per segment,
# at most two segments per robot.
VALUE = {("R1", "s1"): 7, ("R1", "s2"): 5, ("R1", "s3"): 6, ("R1", "s4"): 4, ("R1", "s5"): 5,
         ("R2", "s1"): 6, ("R2", "s2"): 6, ("R2", "s3"): 5, ("R2", "s4"): 5, ("R2", "s5"): 6,
         ("R3", "s1"): 5, ("R3", "s2"): 7, ("R3", "s3"): 6, ("R3", "s4"): 6, ("R3", "s5"): 4,
         ("R4", "s1"): 6, ("R4", "s2"): 5, ("R4", "s3"): 7, ("R4", "s4"): 5, ("R4", "s5"): 6}
ROBOTS = sorted({r for r, _ in VALUE})
SEGMENTS = sorted({s for _, s in VALUE})


def highs_run() -> dict:
    model = mathopt.Model()
    x = {k: model.add_binary_variable(name=f"x_{k[0]}_{k[1]}") for k in sorted(VALUE)}
    for s in SEGMENTS:
        model.add_linear_constraint(sum(x[r, s] for r in ROBOTS) <= 1)
    for r in ROBOTS:
        model.add_linear_constraint(sum(x[r, s] for s in SEGMENTS) <= 2)
    model.maximize(sum(VALUE[k] * x[k] for k in x))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    return {"status": result.termination.reason.name, "objective": round(result.objective_value(), 6),
            "plan": sorted([r, s] for (r, s), v in x.items() if result.variable_values(v) > 0.5)}


def cpsat_run() -> dict:
    model = cp_model.CpModel()
    x = {k: model.new_bool_var(f"x_{k[0]}_{k[1]}") for k in sorted(VALUE)}
    for s in SEGMENTS:
        model.add(sum(x[r, s] for r in ROBOTS) <= 1)
    for r in ROBOTS:
        model.add(sum(x[r, s] for s in SEGMENTS) <= 2)
    model.maximize(sum(VALUE[k] * x[k] for k in x))
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.random_seed = 5
    status = solver.solve(model)
    return {"status": solver.status_name(status), "objective": solver.objective_value,
            "plan": sorted([r, s] for (r, s), v in x.items() if solver.value(v))}


def changing(manifests):
    """A run that returns the given manifests one call at a time."""
    calls = iter(manifests)
    return lambda: next(calls)


BASE = {"status": "OPTIMAL", "objective": 33.0, "plan": [["R1", "s1"], ["R3", "s2"]]}


def test_repeatable_runs_pass_on_highs_and_cpsat_and_a_changing_run_fails():
    for run in (highs_run, cpsat_run):
        digest = assert_deterministic(run, 3)
        assert re.fullmatch(r"[0-9a-f]{64}", digest)
    with pytest.raises(AssertionError):
        assert_deterministic(changing([BASE, {**BASE, "objective": 32.0}]), 2)


def test_a_difference_in_a_later_run_is_caught():
    with pytest.raises(AssertionError):
        assert_deterministic(changing([BASE, BASE, {**BASE, "objective": 31.0}]), 3)
    assert assert_deterministic(changing([BASE, BASE, BASE]), 3)


def test_an_equally_good_other_plan_is_caught():
    tie = {**BASE, "plan": [["R1", "s2"], ["R3", "s1"]]}
    with pytest.raises(AssertionError):
        assert_deterministic(changing([BASE, tie]), 2)
    assert assert_deterministic(changing([BASE, BASE]), 2)


def test_the_failure_names_the_fields_that_changed():
    tie = {**BASE, "plan": [["R1", "s2"], ["R3", "s1"]]}
    with pytest.raises(AssertionError) as caught:
        assert_deterministic(changing([BASE, BASE, tie]), 3)
    assert "run 3" in str(caught.value) and "plan" in str(caught.value)
    assert "objective" not in str(caught.value)
