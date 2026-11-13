import pytest
from ortools.math_opt.python import mathopt

from entry import entry_values


def district(paint_value: float = 0.2) -> mathopt.Model:
    """A school district's repair money ($k): value per $k of each kind of work."""
    model = mathopt.Model(name="district")
    x = {name: model.add_variable(lb=0, name=name) for name in ("roofs", "hvac", "windows", "paint")}
    model.add_linear_constraint(sum(x.values()) <= 100, name="budget")
    model.add_linear_constraint(x["roofs"] <= 50, name="roofers")
    model.add_linear_constraint(x["hvac"] <= 30, name="hvac_crews")
    model.maximize(0.6 * x["roofs"] + 0.5 * x["hvac"] + 0.3 * x["windows"] + paint_value * x["paint"])
    return model


def paint_used(paint_value: float) -> float:
    model = district(paint_value)
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    return result.variable_values(next(v for v in model.variables() if v.name == "paint"))


def test_an_idle_activity_starts_to_pay_above_its_entry_value():
    assert entry_values(district()).get("paint") == pytest.approx(0.3)
    assert paint_used(0.29) == pytest.approx(0)
    assert paint_used(0.31) > 0


def test_activities_in_use_are_not_listed():
    assert set(entry_values(district())) == {"paint"}


def test_in_a_cost_model_the_entry_value_is_below_the_cost():
    model = mathopt.Model(name="fleet")
    vans = model.add_variable(lb=0, name="vans")
    trucks = model.add_variable(lb=0, name="trucks")
    model.add_linear_constraint(vans + trucks >= 10, name="routes")
    model.minimize(2 * vans + 3 * trucks)
    assert entry_values(model).get("trucks") == pytest.approx(2)
