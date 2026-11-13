from ortools.math_opt.python import mathopt

from upgrade import add_bigm_modes, add_hull_modes, mode_variables


def allowed(spend: float, gain: float, rebuild: int) -> bool:
    model = mathopt.Model()
    s, g, r = mode_variables(model)
    add_hull_modes(model, s, g, r)
    for var, value in ((s, spend), (g, gain), (r, rebuild)):
        var.lower_bound = var.upper_bound = value
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


def lp_bound(rows) -> float:
    model = mathopt.Model()
    s, g, r = mode_variables(model, integer=False)
    rows(model, s, g, r)
    model.maximize(3 * g - s)
    return mathopt.solve(model, mathopt.SolverType.GLOP).objective_value()


def test_a_line_crew_gains_at_most_half_its_spend():
    assert allowed(20, 10, rebuild=0) is True
    assert allowed(20, 12, rebuild=0) is False


def test_a_line_crew_spends_at_most_30():
    assert allowed(30, 15, rebuild=0) is True
    assert allowed(40, 15, rebuild=0) is False


def test_a_rebuild_within_its_range_is_allowed():
    assert allowed(60, 40, rebuild=1) is True
    assert allowed(50, 20, rebuild=1) is False


def test_the_hull_bound_is_the_best_plan_and_beats_the_colleagues():
    assert abs(lp_bound(add_hull_modes) - 60) < 1e-6        # the best plan: rebuild, spend 60, gain 40
    assert lp_bound(add_bigm_modes) > 80
