from ortools.math_opt.python import mathopt

from rolling import add_rolling_caps

YEARS = [2027, 2028, 2029, 2030, 2031, 2032]

# Each project's spend by year, $k: dredging, a crane, a berth, a rail spur and new fenders.
WORK = {
    "dredge": {2027: 50, 2028: 50},
    "crane": {2029: 80},
    "berth": {2030: 40, 2031: 40},
    "rail": {2031: 70, 2032: 70},
    "fender": {2030: 40},
}


def allowed(plan: set[str], k: int, cap: int) -> bool:
    model = mathopt.Model()
    x = {name: model.add_binary_variable(name=name) for name in WORK}
    spend = {y: sum(cost.get(y, 0) * x[name] for name, cost in WORK.items()) for y in YEARS}
    add_rolling_caps(model, spend, YEARS, k, cap)
    for name, var in x.items():
        value = 1.0 if name in plan else 0.0
        var.lower_bound = value
        var.upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_plan_within_the_cap_is_allowed_and_one_over_it_refused():
    assert allowed({"dredge", "crane"}, 3, 180) is True
    assert allowed({"dredge", "crane"}, 3, 90) is False


def test_a_plan_that_breaks_only_an_overlapping_window_is_refused():
    assert allowed({"crane"}, 3, 100) is True
    assert allowed({"crane", "berth"}, 3, 100) is False


def test_the_last_full_window_is_capped_too():
    assert allowed({"rail"}, 3, 150) is True
    assert allowed({"rail", "fender"}, 3, 150) is False


def test_a_window_holds_k_years_not_fewer():
    assert allowed({"dredge"}, 3, 150) is True
    assert allowed({"dredge", "crane"}, 3, 150) is False
