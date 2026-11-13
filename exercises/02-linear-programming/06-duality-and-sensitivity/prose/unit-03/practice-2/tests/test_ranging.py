import pytest
from ortools.math_opt.python import mathopt

from ranging import price_range


def depot(hours: float, minimum_y: float = 0):
    """A bus depot's overtime hours: engine work earns 3 per hour (at most 40), brake work 2 (at most 30)."""
    model = mathopt.Model(name="depot")
    engines = model.add_variable(lb=0, ub=40, name="engines")
    brakes = model.add_variable(lb=minimum_y, ub=30, name="brakes")
    row = model.add_linear_constraint(engines + brakes <= hours, name="overtime")
    model.maximize(3 * engines + 2 * brakes)
    return model, row


def test_the_price_holds_up_to_the_next_breakpoint():
    assert price_range(depot, 50, 0, 100)[1] == pytest.approx(70, abs=0.01)
    assert price_range(depot, 20, 0, 100)[1] == pytest.approx(40, abs=0.01)


def test_the_range_reaches_down_to_the_previous_breakpoint():
    assert price_range(depot, 50, 0, 100)[0] == pytest.approx(40, abs=0.01)
    assert price_range(depot, 20, 0, 100)[0] == pytest.approx(0, abs=0.01)


def test_a_price_that_never_changes_reaches_the_search_limit_itself():
    assert price_range(depot, 80, 0, 100) == (pytest.approx(70, abs=0.01), 100)


def test_a_right_hand_side_with_no_plan_ends_the_range():
    assert price_range(lambda h: depot(h, minimum_y=10), 30, 0, 100) == (
        pytest.approx(10, abs=0.01), pytest.approx(50, abs=0.01))
