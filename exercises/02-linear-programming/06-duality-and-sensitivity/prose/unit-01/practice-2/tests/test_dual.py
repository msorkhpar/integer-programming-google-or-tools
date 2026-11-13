import pytest
from ortools.math_opt.python import mathopt

from dual import solve_dual

# A facilities team's week: hours of inspection, repair and painting, value per hour.
VALUE = {"inspect": 4, "repair": 3, "paint": 2}
HOURS = ({"inspect": 1, "repair": 1, "paint": 1}, "<=", 10)
CAP = ({"inspect": 1}, "<=", 6)


def primal_value(value, rows):
    """The LP itself, solved, so every test compares the dual with the real optimum."""
    model = mathopt.Model()
    x = {a: model.add_variable(lb=0, name=a) for a in value}
    for name, (coeffs, sense, rhs) in rows.items():
        lhs = sum(c * x[a] for a, c in coeffs.items())
        model.add_linear_constraint(lhs <= rhs if sense == "<=" else lhs >= rhs if sense == ">=" else lhs == rhs)
    model.maximize(sum(v * x[a] for a, v in value.items()))
    return mathopt.solve(model, mathopt.SolverType.GLOP).objective_value()


def test_the_dual_value_equals_the_optimum_and_prices_the_rows():
    rows = {"hours": HOURS, "inspect_cap": CAP}
    bound, prices = solve_dual(VALUE, rows)
    assert bound == pytest.approx(primal_value(VALUE, rows)) == pytest.approx(36)
    assert prices == pytest.approx({"hours": 3, "inspect_cap": 1})


def test_a_minimum_row_gets_a_price_at_most_zero():
    rows = {"hours": HOURS, "inspect_cap": CAP, "min_repair": ({"repair": 1}, ">=", 5)}
    bound, prices = solve_dual(VALUE, rows)
    assert bound == pytest.approx(primal_value(VALUE, rows)) == pytest.approx(35)
    assert prices["min_repair"] == pytest.approx(-1)


def test_an_equality_row_may_get_a_negative_price():
    rows = {"hours": HOURS, "inspect_cap": CAP, "contract": ({"paint": 1}, "==", 1)}
    bound, prices = solve_dual(VALUE, rows)
    assert bound == pytest.approx(primal_value(VALUE, rows)) == pytest.approx(35)
    assert prices["contract"] == pytest.approx(-1)


def test_an_activity_in_no_row_gets_a_cover_row_all_the_same():
    rows = {"hours": ({"inspect": 1, "repair": 1}, "<=", 10)}
    assert solve_dual({"inspect": 4, "repair": 3, "paint": 2}, rows) == (None, {})
    bound, prices = solve_dual({"inspect": 4, "repair": 3, "paint": 0}, rows)
    assert bound == pytest.approx(40)
    assert prices == pytest.approx({"hours": 4})


def test_each_cover_row_weights_prices_by_the_activitys_coefficients():
    rows = {"hours": ({"inspect": 2, "repair": 1, "paint": 1}, "<=", 16), "inspect_cap": CAP}
    bound, prices = solve_dual(VALUE, rows)
    assert bound == pytest.approx(primal_value(VALUE, rows)) == pytest.approx(48)
    assert prices == pytest.approx({"hours": 3, "inspect_cap": 0})
