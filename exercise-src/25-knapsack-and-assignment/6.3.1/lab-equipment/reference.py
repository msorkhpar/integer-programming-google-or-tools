from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Analyzer:
    aid: str
    value: int        # tests per day it adds
    price: int        # $k
    area: float       # floor space, m^2
    load: float       # electrical load, kW


def add_lab_rules(model: mathopt.Model, x: dict, analyzers: list[Analyzer], budget: int, floor: float,
                  power: float, lease_rate: float, max_lease: float) -> None:
    """Price and lease within the budget, area within owned plus leased floor, load within the supply."""
    lease = model.add_variable(lb=0, ub=max_lease, name="lease")
    model.add_linear_constraint(sum(a.price * x[a.aid] for a in analyzers) + lease_rate * lease <= budget,
                                name="budget")
    model.add_linear_constraint(sum(a.area * x[a.aid] for a in analyzers) <= floor + lease, name="floor")
    model.add_linear_constraint(sum(a.load * x[a.aid] for a in analyzers) <= power, name="power")


def build(analyzers: list[Analyzer], budget: int, floor: float, power: float, lease_rate: float,
          max_lease: float) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="lab-equipment")
    x = {a.aid: model.add_binary_variable(name=f"x_{a.aid}") for a in analyzers}
    add_lab_rules(model, x, analyzers, budget, floor, power, lease_rate, max_lease)
    model.maximize(sum(a.value * x[a.aid] for a in analyzers))
    return model, x


if __name__ == "__main__":
    pair = [Analyzer("H1", 400, 120, 6.0, 3.0), Analyzer("C1", 900, 300, 9.0, 7.5)]
    model, x = build(pair, 500, 12.0, 10.0, 4.0, 5.0)
    print(len(list(model.linear_constraints())), "rows")
