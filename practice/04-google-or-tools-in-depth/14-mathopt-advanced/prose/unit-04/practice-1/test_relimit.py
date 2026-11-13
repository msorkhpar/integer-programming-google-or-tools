import math

from ortools.math_opt.python import mathopt

from relimit import replace_upper


def heating(on_zero: bool = False, lower: float | None = 40.0):
    """A district heating plant's boiler rule, not the lesson's portfolio."""
    model = mathopt.Model()
    z = model.add_binary_variable(name="run_b1")
    heat = model.add_variable(lb=0, ub=200, name="heat_b1")
    gas = model.add_variable(lb=0, ub=500, name="gas_b1")
    other = model.add_indicator_constraint(indicator=z, implied_constraint=gas <= 400, name="gas_cap")
    ic = model.add_indicator_constraint(indicator=z, activate_on_zero=on_zero, implied_expr=heat + 0.5 * gas,
                                        implied_lb=lower, implied_ub=120, name="boiler_b1")
    return model, ic, other


def terms(ic) -> dict[str, float]:
    return {t.variable.name: t.coefficient for t in ic.terms()}


def test_the_new_constraint_has_the_new_limit_and_the_same_indicator():
    model, ic, _ = heating()
    new = replace_upper(model, ic, 100)
    assert new.upper_bound == 100
    assert new.indicator_variable.name == "run_b1" and new.name == "boiler_b1"
    assert terms(new) == {"heat_b1": 1.0, "gas_b1": 0.5}


def test_the_old_constraint_is_gone():
    model, ic, other = heating()
    old_id = ic.id
    replace_upper(model, ic, 100)
    assert model.get_num_indicator_constraints() == 2
    assert not model.has_indicator_constraint(old_id)
    assert model.has_indicator_constraint(other.id)


def test_a_rule_switched_on_at_zero_stays_so():
    model, ic, _ = heating(on_zero=True)
    new = replace_upper(model, ic, 90)
    assert (new.upper_bound, new.activate_on_zero) == (90, True)


def test_the_lower_bound_is_kept():
    model, ic, _ = heating(lower=40)
    new = replace_upper(model, ic, 100)
    assert (new.lower_bound, new.upper_bound) == (40, 100)
    model2, ic2, _ = heating(lower=None)
    assert replace_upper(model2, ic2, 100).lower_bound == -math.inf
