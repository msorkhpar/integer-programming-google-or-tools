from ortools.math_opt.python import mathopt

from extremes import matrix_extremes


def staffing() -> tuple[mathopt.Model, dict]:
    model = mathopt.Model()
    v = {name: model.add_variable(lb=0, ub=100, name=name) for name in ("nurses", "doctors", "beds")}
    model.add_linear_constraint(52_000 * v["nurses"] + 95_000 * v["doctors"] <= 9_000_000, name="payroll")
    model.add_linear_constraint(0.25 * v["doctors"] + v["nurses"] >= 40, name="cover")
    model.add_linear_constraint(v["beds"] <= 400, name="ward")
    return model, v


def test_the_smallest_and_largest_entries_are_named_by_row_and_variable():
    model, _ = staffing()
    smallest, largest = matrix_extremes(model)
    assert smallest == ("cover", "doctors", 0.25)
    assert largest == ("payroll", "doctors", 95_000)


def test_size_is_measured_without_the_sign():
    model, v = staffing()
    model.add_linear_constraint(-0.01 * v["beds"] + v["nurses"] <= 50, name="night")
    model.add_linear_constraint(-2e6 * v["nurses"] >= -1e9, name="bonus")
    smallest, largest = matrix_extremes(model)
    assert smallest == ("night", "beds", -0.01)
    assert largest == ("bonus", "nurses", -2e6)


def test_objective_coefficients_are_not_matrix_entries():
    model, v = staffing()
    model.minimize(1e9 * v["doctors"] + 0.001 * v["beds"])
    smallest, largest = matrix_extremes(model)
    assert smallest == ("cover", "doctors", 0.25)
    assert largest == ("payroll", "doctors", 95_000)


def test_variable_bounds_are_not_matrix_entries():
    model, v = staffing()
    v["beds"].upper_bound = 1e12
    v["nurses"].lower_bound = 0.0001
    smallest, largest = matrix_extremes(model)
    assert smallest == ("cover", "doctors", 0.25)
    assert largest == ("payroll", "doctors", 95_000)
