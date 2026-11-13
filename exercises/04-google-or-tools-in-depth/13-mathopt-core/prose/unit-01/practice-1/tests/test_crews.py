from ortools.math_opt.python import mathopt

from crews import Depot, build

# A water utility's depots, not the lesson's portfolio.
DEPOTS = [Depot("Harbor", 3, 4.0, 9.0), Depot("Mill", 2, 3.0, 7.0), Depot("Ridge", 4, 5.0, 2.0)]
LOW, HIGH = 4, 6


def allowed(open_plan: dict[str, int], crew_plan: dict[str, float]) -> bool:
    """Fix every variable to the plan and ask whether the model accepts it."""
    model, open_, crews = build(DEPOTS, LOW, HIGH)
    for name, var in open_.items():
        var.lower_bound = var.upper_bound = open_plan.get(name, 0)
    for name, var in crews.items():
        var.lower_bound = var.upper_bound = crew_plan.get(name, 0)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


ALL_OPEN = {"Harbor": 1, "Mill": 1, "Ridge": 1}


def test_each_variable_has_its_domain():
    model, open_, crews = build(DEPOTS, LOW, HIGH)
    for d in DEPOTS:
        o, c = open_[d.name], crews[d.name]
        assert (o.lower_bound, o.upper_bound) == (0, 1)
        assert (c.lower_bound, c.upper_bound) == (0, d.cap)


def test_a_plan_inside_the_band_is_allowed_and_one_above_it_refused():
    assert allowed(ALL_OPEN, {"Harbor": 2, "Mill": 1, "Ridge": 2}) is True
    assert allowed(ALL_OPEN, {"Harbor": 3, "Mill": 2, "Ridge": 2}) is False


def test_the_cheapest_plan_is_found():
    model, open_, crews = build(DEPOTS, LOW, HIGH)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    assert result.termination.reason == mathopt.TerminationReason.OPTIMAL
    # Ridge alone hosts 4 crews: 4 * 5.0 + 2.0 = 22.0; Mill 2 + Ridge 2 costs 6 + 7 + 10 + 2 = 25.
    assert abs(result.objective_value() - 22.0) < 1e-6
    assert round(result.variable_values(crews["Ridge"])) == 4


def test_too_few_crews_are_refused():
    assert allowed({"Ridge": 1}, {"Ridge": 4}) is True
    assert allowed({"Ridge": 1}, {"Ridge": 3}) is False


def test_a_closed_depot_hosts_no_crews():
    assert allowed({"Ridge": 1, "Mill": 1}, {"Ridge": 3, "Mill": 1}) is True
    assert allowed({"Ridge": 1}, {"Ridge": 3, "Mill": 1}) is False


def test_a_fractional_crew_is_refused():
    assert allowed({"Ridge": 1, "Mill": 1}, {"Ridge": 3, "Mill": 2}) is True
    assert allowed({"Ridge": 1, "Mill": 1}, {"Ridge": 3, "Mill": 1.5}) is False
