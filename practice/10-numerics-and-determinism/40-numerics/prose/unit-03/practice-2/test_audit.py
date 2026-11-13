import pytest
from ortools.math_opt.python import mathopt

from audit import audit


def depots():
    """Open depots (binary) and ship trucks (continuous, 0 to 40) under a capacity and a demand row."""
    model = mathopt.Model()
    north = model.add_binary_variable(name="open_north")
    south = model.add_binary_variable(name="open_south")
    trucks = model.add_variable(lb=0, ub=40, name="trucks")
    model.add_linear_constraint(trucks <= 25 * north + 25 * south, name="capacity")
    model.add_linear_constraint(lb=10.0, ub=30.0, expr=trucks, name="demand")
    return model, north, south, trucks


def test_a_clean_plan_has_no_violations_and_a_broken_one_reports_each_kind():
    model, north, south, trucks = depots()
    assert audit(model, {north: 1.0, south: 0.0, trucks: 20.0}) == {"bound": 0.0, "integrality": 0.0, "row": 0.0}
    found = audit(model, {north: 1.0, south: 3e-7, trucks: 41.0})
    assert found["bound"] == pytest.approx(1.0)
    assert found["integrality"] == pytest.approx(3e-7)
    assert found["row"] == pytest.approx(16.0 - 25 * 3e-7)


def test_integrality_is_the_distance_to_the_nearest_whole_number():
    model, north, south, trucks = depots()
    found = audit(model, {north: 0.9999996, south: 0.0, trucks: 20.0})
    assert found["integrality"] == pytest.approx(4e-7)


def test_continuous_variables_have_no_integrality():
    model, north, south, trucks = depots()
    found = audit(model, {north: 1.0, south: 0.0, trucks: 12.5})
    assert found["integrality"] == 0.0


def test_lower_bounds_and_lower_sides_count_too():
    model, north, south, trucks = depots()
    found = audit(model, {north: 1.0, south: -2e-9, trucks: 6.0})
    assert found["bound"] == pytest.approx(2e-9)
    assert found["row"] == pytest.approx(4.0)
