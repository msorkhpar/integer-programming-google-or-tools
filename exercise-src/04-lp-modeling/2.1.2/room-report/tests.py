import pytest
from ortools.math_opt.python import mathopt

from report import binding, room


def pumping(p1: float, p2: float):
    """Two pumps whose output is fixed by their bounds, so the solve returns exactly (p1, p2)."""
    model = mathopt.Model(name="pumping")
    x = model.add_variable(lb=p1, ub=p1, name="p1")
    y = model.add_variable(lb=p2, ub=p2, name="p2")
    model.add_linear_constraint(x + 2 * y <= 100, name="energy")
    model.add_linear_constraint(x + y >= 30, name="contract")
    model.add_linear_constraint(lb=10, ub=40, expr=x - y, name="balance")
    model.add_linear_constraint(x == 2 * y, name="ratio")
    model.maximize(x + y)
    return model, mathopt.solve(model, mathopt.SolverType.GLOP)


def test_slack_of_an_at_most_row_and_the_binding_list():
    model, result = pumping(40, 20)
    assert room(model, result)["energy"] == pytest.approx(20)
    assert room(model, result)["ratio"] == pytest.approx(0)
    assert "ratio" in binding(model, result)
    assert "energy" not in binding(model, result)


def test_the_surplus_of_an_at_least_row_is_positive():
    model, result = pumping(40, 20)
    assert room(model, result)["contract"] == pytest.approx(30)


def test_a_ranged_row_reports_its_room_to_the_nearer_bound():
    model, result = pumping(40, 20)
    assert room(model, result)["balance"] == pytest.approx(10)
    model, result = pumping(20, 10)
    assert room(model, result)["balance"] == pytest.approx(0)


def test_a_row_off_its_bound_only_by_rounding_noise_is_binding():
    model = mathopt.Model()
    x = model.add_variable(lb=0.1, ub=0.1, name="x")
    y = model.add_variable(lb=0.2, ub=0.2, name="y")
    model.add_linear_constraint(x + y >= 0.3, name="minimum")
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    assert binding(model, result) == ["minimum"]
