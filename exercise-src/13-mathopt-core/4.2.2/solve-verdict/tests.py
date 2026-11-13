import pytest
from ortools.math_opt.python import mathopt

from verdict import verdict

S, R = mathopt.SolverType, mathopt.TerminationReason


def roster(min_shifts: int = 3) -> mathopt.Model:
    """Pick nurse shifts (value per shift) under a weekly hours cap: a small knapsack of its own."""
    hours = [9, 7, 11, 5, 8, 12, 6, 10, 4, 9, 7, 13, 8, 6, 11]
    value = [14, 10, 17, 6, 12, 19, 8, 15, 5, 13, 11, 21, 12, 9, 16]
    model = mathopt.Model(name="roster")
    x = [model.add_binary_variable(name=f"s{i}") for i in range(len(hours))]
    model.add_linear_constraint(mathopt.fast_sum(h * v for h, v in zip(hours, x)) <= 47, name="hours")
    model.add_linear_constraint(mathopt.fast_sum(x) >= min_shifts, name="cover")
    model.maximize(mathopt.fast_sum(c * v for c, v in zip(value, x)))
    return model


def open_ended() -> mathopt.Model:
    model = mathopt.Model(name="open-ended")
    a = model.add_variable(lb=0, name="a")
    b = model.add_variable(lb=0, ub=3, name="b")
    model.add_linear_constraint(b - a <= 1, name="r")
    model.maximize(a + b)
    return model


def test_an_optimal_solve_is_used_with_no_gap():
    result = mathopt.solve(roster(), S.HIGHS)
    v = verdict(result)
    assert (v.action, v.gap, v.limit) == ("use", 0.0, None)
    assert v.value == pytest.approx(result.objective_value())


def test_an_infeasible_solve_is_a_conflict_with_no_value():
    v = verdict(mathopt.solve(roster(min_shifts=12), S.HIGHS))
    assert (v.action, v.value, v.gap, v.limit) == ("conflict", None, None, None)


def test_a_limited_solve_with_a_plan_reports_its_gap_and_limit():
    result = mathopt.solve(roster(), S.GSCIP, params=mathopt.SolveParameters(solution_limit=1))
    assert result.termination.reason == R.FEASIBLE
    v = verdict(result)
    assert (v.action, v.limit) == ("use-with-gap", "SOLUTION")
    assert v.value == pytest.approx(result.objective_value())
    assert v.gap == pytest.approx(abs(result.dual_bound() - result.primal_bound()))
    assert v.gap > 0


def test_a_limited_solve_without_a_plan_says_which_limit():
    lp = roster()
    for var in lp.variables():
        var.integer = False
    result = mathopt.solve(lp, S.HIGHS, params=mathopt.SolveParameters(iteration_limit=1))
    assert result.termination.reason == R.NO_SOLUTION_FOUND
    v = verdict(result)
    assert (v.action, v.value, v.limit) == ("retry", None, "ITERATION")


def test_an_unbounded_solve_is_a_model_error_even_with_a_plan():
    result = mathopt.solve(open_ended(), S.HIGHS)
    assert result.termination.reason == R.UNBOUNDED and result.has_primal_feasible_solution()
    v = verdict(result)
    assert (v.action, v.value) == ("model-error", None)


def test_infeasible_or_unbounded_is_a_model_error():
    result = mathopt.solve(open_ended(), S.GLOP)
    assert result.termination.reason == R.INFEASIBLE_OR_UNBOUNDED
    assert verdict(result).action == "model-error"


def test_solver_failures_are_reported_as_solver_errors():
    for reason in (R.IMPRECISE, R.NUMERICAL_ERROR, R.OTHER_ERROR):
        result = mathopt.SolveResult(termination=mathopt.Termination(reason=reason))
        v = verdict(result)
        assert (v.action, v.value) == ("solver-error", None)
