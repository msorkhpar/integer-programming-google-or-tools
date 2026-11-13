from ortools.math_opt.python import mathopt

from compare_models import same_model


def make(order=("x", "y", "z"), coef=5.0, integer=True, cap=10.0, maximize=True, with_z=True):
    model = mathopt.Model(name="m")
    v = {name: model.add_variable(lb=0, ub=1, is_integer=integer, name=name) for name in order}
    terms = 2.0 * v["x"] + coef * v["y"] + (1.0 * v["z"] if with_z else 0.0)
    model.add_linear_constraint(terms <= cap, name="cap")
    model.add_linear_constraint(v["x"] + v["y"] <= 1, name="pick")
    goal = 4.0 * v["x"] + 3.0 * v["y"] + 1.5 * v["z"]
    model.maximize(goal) if maximize else model.minimize(goal)
    return model


def test_order_does_not_matter_and_a_changed_coefficient_does():
    assert same_model(make(), make(order=("z", "y", "x"))) is True
    assert same_model(make(), make(coef=6.0)) is False


def test_coefficients_equal_up_to_rounding_count_as_equal():
    assert same_model(make(), make(coef=5.0 * (1 + 1e-12))) is True
    assert same_model(make(), make(coef=5.0 * (1 + 1e-6))) is False


def test_a_term_missing_from_one_model_is_a_difference():
    assert same_model(make(), make(order=("z", "x", "y"))) is True
    assert same_model(make(), make(with_z=False)) is False


def test_integrality_is_part_of_the_model():
    assert same_model(make(integer=False), make(integer=False, order=("y", "x", "z"))) is True
    assert same_model(make(), make(integer=False)) is False


def test_the_objective_sense_is_part_of_the_model():
    assert same_model(make(maximize=False), make(maximize=False, order=("y", "z", "x"))) is True
    assert same_model(make(), make(maximize=False)) is False


def test_a_row_bound_is_part_of_the_model():
    assert same_model(make(cap=10.0), make(cap=10.0, order=("x", "z", "y"))) is True
    assert same_model(make(), make(cap=11.0)) is False
