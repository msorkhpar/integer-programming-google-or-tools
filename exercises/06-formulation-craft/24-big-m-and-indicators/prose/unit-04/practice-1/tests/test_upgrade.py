from ortools.math_opt.python import mathopt

from upgrade import add_bigm_modes, mode_variables


def allowed(spend: float, gain: float, rebuild: int) -> bool:
    model = mathopt.Model()
    s, g, r = mode_variables(model)
    add_bigm_modes(model, s, g, r)
    for var, value in ((s, spend), (g, gain), (r, rebuild)):
        var.lower_bound = var.upper_bound = value
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_line_crew_gains_at_most_half_its_spend():
    assert allowed(20, 10, rebuild=0) is True
    assert allowed(20, 12, rebuild=0) is False


def test_a_line_crew_spends_at_most_30():
    assert allowed(30, 15, rebuild=0) is True
    assert allowed(40, 15, rebuild=0) is False


def test_a_rebuild_spends_at_least_60():
    assert allowed(80, 40, rebuild=1) is True
    assert allowed(50, 20, rebuild=1) is False


def test_a_rebuild_may_gain_more_than_half_its_spend():
    assert allowed(60, 40, rebuild=1) is True
    assert allowed(60, 40, rebuild=0) is False


def test_the_rows_are_as_tight_as_the_bounds_allow():
    model = mathopt.Model()
    s, g, r = mode_variables(model, integer=False)
    add_bigm_modes(model, s, g, r)
    model.maximize(3 * g - s)
    bound = mathopt.solve(model, mathopt.SolverType.GLOP).objective_value()
    assert 60 - 1e-6 <= bound < 81          # 60 is the best plan; a big-M with M = 1,000 gives 110
