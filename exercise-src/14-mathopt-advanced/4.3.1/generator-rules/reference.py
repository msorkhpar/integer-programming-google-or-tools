from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Unit:
    name: str
    min_mw: float
    max_mw: float


def add_unit_rules(model: mathopt.Model, on: dict, power: dict, units: list[Unit]) -> None:
    """Off makes no power; on runs between the unit's minimum and maximum."""
    for u in units:
        model.add_indicator_constraint(indicator=on[u.name], activate_on_zero=True,
                                       implied_constraint=power[u.name] <= 0, name=f"off_{u.name}")
        model.add_indicator_constraint(indicator=on[u.name], implied_constraint=power[u.name] >= u.min_mw,
                                       name=f"on_{u.name}")


def build(units: list[Unit], demand: float) -> tuple[mathopt.Model, dict, dict]:
    model = mathopt.Model(name="island hour")
    on = {u.name: model.add_binary_variable(name=f"on_{u.name}") for u in units}
    power = {u.name: model.add_variable(lb=0, ub=u.max_mw, name=f"p_{u.name}") for u in units}
    add_unit_rules(model, on, power, units)
    model.add_linear_constraint(sum(power.values()) >= demand, name="demand")
    model.minimize(sum(on.values()))
    return model, on, power


if __name__ == "__main__":
    model, on, power = build([Unit("D1", 10, 40), Unit("D2", 25, 60)], 50)
    print(model.get_num_indicator_constraints(), "indicator constraints")
