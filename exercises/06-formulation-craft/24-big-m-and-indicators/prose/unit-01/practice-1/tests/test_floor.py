from ortools.math_opt.python import mathopt

from floor import add_floor, spend_variables

ORDERS = {"trim": (0, 60), "poles": (20, 80)}
WITH_CREDIT = {"trim": (0, 60), "poles": (20, 80), "credit": (-30, 0)}


def allowed(values: dict[str, float], waiver: int, items=ORDERS, floor: float = 100) -> bool:
    model = mathopt.Model()
    spend = spend_variables(model, items)
    w = model.add_binary_variable(name="waiver")
    add_floor(model, spend, floor, w)
    for name, var in spend.items():                 # fix the plan only after the row is written
        var.lower_bound = var.upper_bound = values[name]
    w.lower_bound = w.upper_bound = waiver
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


def test_without_a_waiver_the_floor_holds():
    assert allowed({"trim": 50, "poles": 50}, waiver=0) is True
    assert allowed({"trim": 40, "poles": 50}, waiver=0) is False


def test_a_waiver_allows_the_lowest_spend_the_orders_allow():
    assert allowed({"trim": 0, "poles": 20}, waiver=1) is True
    assert allowed({"trim": 0, "poles": 20}, waiver=0) is False


def test_a_credit_line_can_take_the_total_below_zero_under_a_waiver():
    assert allowed({"trim": 0, "poles": 20, "credit": -30}, waiver=1, items=WITH_CREDIT) is True
    assert allowed({"trim": 0, "poles": 20, "credit": -30}, waiver=0, items=WITH_CREDIT) is False


def test_the_row_is_as_tight_as_the_bounds_allow():
    # A half waiver in the LP relaxation: the least total spend the row then allows.
    model = mathopt.Model()
    spend = spend_variables(model, ORDERS)
    w = model.add_variable(lb=0.5, ub=0.5, name="waiver")
    add_floor(model, spend, 100, w)
    model.minimize(sum(spend.values()))
    least = mathopt.solve(model, mathopt.SolverType.GLOP).objective_value()
    assert abs(least - 60) < 1e-6        # halfway between the floor, 100, and the lowest spend, 20
