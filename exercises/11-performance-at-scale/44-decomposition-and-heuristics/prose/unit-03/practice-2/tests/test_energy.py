from ortools.math_opt.python import mathopt

from energy import add_energy_rows

# (crane days, first day allowed, day it must end by), in a 20-day month
LIFTS = {
    "breaker A": (6, 0, 8), "breaker B": (5, 2, 9), "transformer": (9, 0, 20),
    "bus section": (4, 12, 18), "reactor": (5, 11, 20), "spare": (2, 0, 20),
}


def allowed(month: set[str]) -> bool:
    model = mathopt.Model()
    x = {n: model.add_binary_variable(name=n) for n in LIFTS}
    add_energy_rows(model, x, LIFTS)
    for n, var in x.items():
        value = 1.0 if n in month else 0.0
        var.lower_bound = value
        var.upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_light_month_is_allowed_and_an_overfull_month_refused():
    assert allowed({"bus section", "spare"}) is True
    assert allowed({"transformer", "breaker A", "bus section", "spare", "reactor"}) is False


def test_lifts_crowded_into_a_short_window_are_refused():
    assert allowed({"breaker A", "breaker B"}) is False
    assert allowed({"breaker B", "spare", "reactor"}) is True


def test_lifts_that_only_overlap_a_window_are_not_counted_in_it():
    # transformer's window covers the whole month, so it may run after the breakers' stretch
    assert allowed({"breaker A", "transformer"}) is True
    assert allowed({"breaker B", "transformer", "spare"}) is True
    assert allowed({"breaker A", "breaker B", "transformer"}) is False


def allowed_in(lifts: dict, month: set[str]) -> bool:
    model = mathopt.Model()
    x = {n: model.add_binary_variable(name=n) for n in lifts}
    add_energy_rows(model, x, lifts)
    for n, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if n in month else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_stretch_from_day_a_to_day_b_holds_b_minus_a_days():
    # all three may use days 0 to 7: eight crane days, no more
    lifts = {"pump": (4, 0, 8), "valve": (4, 0, 8), "gate": (5, 0, 8)}
    assert allowed_in(lifts, {"pump", "valve"}) is True
    assert allowed_in(lifts, {"pump", "gate"}) is False


def test_a_stretch_with_no_lift_inside_gets_no_row():
    model = mathopt.Model()
    x = {n: model.add_binary_variable(name=n) for n in LIFTS}
    rows = add_energy_rows(model, x, LIFTS)
    assert (0, 8) in rows and (2, 9) in rows
    assert (2, 8) not in rows and (12, 9) not in rows
