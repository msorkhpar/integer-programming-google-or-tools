import pytest
from ortools.math_opt.python import mathopt

from renewals import coefficients, objective

# A water utility: breaks avoided, leakage avoided (megalitres), NPV ($k).
# Each reference is the board's swing, here equal to the largest benefit of these four rows.
REFERENCE = {"breaks": 4.0, "leakage": 200.0, "npv": 1_000.0}
WEIGHTS = {"breaks": 0.4, "leakage": 0.2, "npv": 0.4}
BENEFITS = {
    ("Elm", 2028): {"breaks": 2.0, "leakage": 50.0, "npv": 300.0},       # 0.2 + 0.05 + 0.12 = 0.37 -> 925
    ("Oak", 2029): {"breaks": 4.0, "leakage": 0.0, "npv": 100.0},        # 0.4 + 0 + 0.04 = 0.44 -> 1,100
    ("Ash", 2028): {"breaks": 0.0, "leakage": 200.0, "npv": 1_000.0},    # 0 + 0.2 + 0.4 = 0.60 -> 1,500
    ("Yew", 2030): {"breaks": 0.0, "leakage": 0.0, "npv": 0.0},          # nothing -> 0
}


def plan_value(x, coefficient, plan):
    values = {var: 1.0 if key in plan else 0.0 for key, var in x.items()}
    return mathopt.evaluate_expression(objective(x, coefficient), values)


def start_variables(keys):
    model = mathopt.Model()
    return {key: model.add_binary_variable(name=f"x_{key[0]}_{key[1]}") for key in keys}


def test_each_coefficient_is_npv_equivalent_dollars():
    c = coefficients(BENEFITS, REFERENCE, WEIGHTS)
    assert c == pytest.approx({("Elm", 2028): 925.0, ("Oak", 2029): 1_100.0, ("Ash", 2028): 1_500.0, ("Yew", 2030): 0.0})


def test_the_objective_is_the_sum_over_the_chosen_starts():
    c = coefficients(BENEFITS, REFERENCE, WEIGHTS)
    x = start_variables(c)
    assert plan_value(x, c, {("Elm", 2028), ("Ash", 2028)}) == pytest.approx(2_425.0)
    assert plan_value(x, c, set()) == pytest.approx(0.0)


def test_each_start_year_keeps_its_own_coefficient():
    later = {**BENEFITS, ("Elm", 2030): {"breaks": 1.0, "leakage": 40.0, "npv": 200.0}}   # 0.1 + 0.04 + 0.08
    c = coefficients(later, REFERENCE, WEIGHTS)
    assert c[("Elm", 2030)] == pytest.approx(550.0)
    assert c[("Elm", 2028)] == pytest.approx(925.0)


def test_a_new_candidate_changes_no_other_coefficient():
    bigger = {**BENEFITS, ("Fir", 2029): {"breaks": 8.0, "leakage": 400.0, "npv": 50.0}}
    c = coefficients(bigger, REFERENCE, WEIGHTS)
    assert c[("Oak", 2029)] == pytest.approx(1_100.0)
    assert c[("Fir", 2029)] == pytest.approx(3_050.0)                                  # 0.8 + 0.4 + 0.02 = 1.22
