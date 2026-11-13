import pytest
from ortools.sat.python import cp_model

from roster_outcome import outcome


def solve_two_crews(weeks_needed: int):
    """Two crews, up to 3 weeks each; maximize 5 * weeks worked; require `weeks_needed` weeks in total."""
    model = cp_model.CpModel()
    a, b = model.new_int_var(0, 3, "a"), model.new_int_var(0, 3, "b")
    model.add(a + b == weeks_needed)
    model.maximize(5 * a + 5 * b)
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    return status, solver.objective_value, solver.best_objective_bound


def test_a_proven_roster_is_optimal_with_no_gap():
    status, objective, bound = solve_two_crews(4)
    out = outcome(status, objective, bound, 30)
    assert (out["status"], out["value"], out["gap"]) == ("optimal", 20.0, 0.0)


def test_a_roster_stopped_by_the_limit_is_time_limit_with_its_gap():
    out = outcome(cp_model.FEASIBLE, 80.0, 100.0, 30)
    assert out["status"] == "time_limit" and out["value"] == 80.0


def test_the_gap_is_measured_against_the_roster_found():
    assert outcome(cp_model.FEASIBLE, 80.0, 100.0, 30)["gap"] == pytest.approx(0.25)


def test_no_roster_within_the_limit_is_not_infeasible():
    out = outcome(cp_model.UNKNOWN, 0.0, 100.0, 30)
    assert out["status"] == "time_limit" and out["value"] is None and out["gap"] is None


def test_an_impossible_roster_is_infeasible():
    status, objective, bound = solve_two_crews(7)
    out = outcome(status, objective, bound, 30)
    assert out["status"] == "infeasible" and out["value"] is None


def test_a_refused_model_is_failed():
    out = outcome(cp_model.MODEL_INVALID, 0.0, 0.0, 30)
    assert out["status"] == "failed" and out["value"] is None
