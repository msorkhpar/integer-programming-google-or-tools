from ortools.math_opt.python import mathopt

from keep import keep_within

REL1 = mathopt.ObjectiveParameters(objective_degradation_relative_tolerance=0.01)


def allowed(value: float, best: float, is_maximize: bool, params) -> bool:
    """A fleet's on-time score (or cost) fixed at `value`: does the kept row accept it?"""
    model = mathopt.Model()
    score = model.add_variable(lb=-1e6, ub=1e6, name="score")
    keep_within(model, 2 * score, best, is_maximize, params)       # the objective is 2 * score
    score.lower_bound = score.upper_bound = value / 2
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_maximized_objective_may_fall_by_its_relative_tolerance():
    assert allowed(990, 1000, True, REL1) is True
    assert allowed(989, 1000, True, REL1) is False


def test_a_minimized_objective_may_rise_by_its_absolute_tolerance():
    params = mathopt.ObjectiveParameters(objective_degradation_absolute_tolerance=5)
    assert allowed(1005, 1000, False, params) is True
    assert allowed(900, 1000, False, params) is True
    assert allowed(1006, 1000, False, params) is False


def test_no_tolerance_keeps_the_best_value():
    assert allowed(1000, 1000, True, None) is True
    assert allowed(999, 1000, True, None) is False


def test_a_negative_best_uses_its_size():
    assert allowed(-1010, -1000, True, REL1) is True
    assert allowed(-1011, -1000, True, REL1) is False


def test_with_both_tolerances_the_larger_loss_applies():
    params = mathopt.ObjectiveParameters(objective_degradation_absolute_tolerance=50,
                                         objective_degradation_relative_tolerance=0.01)
    assert allowed(950, 1000, True, params) is True
    assert allowed(949, 1000, True, params) is False
