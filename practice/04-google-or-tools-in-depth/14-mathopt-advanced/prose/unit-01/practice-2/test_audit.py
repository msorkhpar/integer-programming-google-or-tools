import math

from ortools.math_opt.python import mathopt

from audit import audit


def model_with(*rules):
    """A pump station's rules, not the lesson's portfolio: (name, on_zero, lb, ub, coefficients)."""
    model = mathopt.Model()
    pump = model.add_binary_variable(name="pump")
    flow = model.add_variable(lb=0, ub=500, name="flow")
    level = model.add_variable(lb=0, ub=20, name="level")
    named = {"flow": flow, "level": level}
    for name, on_zero, lb, ub, coefs in rules:
        expr = sum(c * named[v] for v, c in coefs.items())
        model.add_indicator_constraint(indicator=pump, activate_on_zero=on_zero, implied_expr=expr,
                                       implied_lb=lb, implied_ub=ub, name=name)
    return model


def test_a_one_sided_rule_switched_on_at_one():
    model = model_with(("max_flow", False, None, 300, {"flow": 1}))
    assert audit(model) == [("max_flow", "pump", 1, -math.inf, 300.0, {"flow": 1.0})]


def test_a_rule_switched_on_at_zero_lists_zero():
    model = model_with(("no_flow", True, None, 0, {"flow": 1}), ("max_flow", False, None, 300, {"flow": 1}))
    assert [(name, active) for name, _, active, *_ in audit(model)] == [("no_flow", 0), ("max_flow", 1)]


def test_a_two_sided_rule_keeps_both_bounds():
    model = model_with(("band", False, 4, 12, {"level": 1}))
    assert [row[3:5] for row in audit(model)] == [(4.0, 12.0)]


def test_coefficients_are_the_rule_s_own():
    model = model_with(("mix", False, None, 900, {"flow": 2, "level": 15}))
    assert audit(model) == [("mix", "pump", 1, -math.inf, 900.0, {"flow": 2.0, "level": 15.0})]
