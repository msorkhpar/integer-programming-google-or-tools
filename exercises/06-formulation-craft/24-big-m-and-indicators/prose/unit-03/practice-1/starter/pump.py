from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def pump_variables(model: mathopt.Model) -> tuple[mathopt.Variable, mathopt.Variable]:
    """The pump's flow (no upper bound: the station has no rated maximum on record) and its on/off binary."""
    flow = model.add_variable(lb=0, ub=math.inf, name="flow")
    on = model.add_binary_variable(name="on")
    return flow, on


def add_pump_rules(model: mathopt.Model, flow: mathopt.Variable, on: mathopt.Variable, min_flow: float) -> None:
    """An idle pump moves nothing; a running pump moves at least `min_flow`."""
    # TODO: your rules, as indicator constraints.
    return None

if __name__ == "__main__":
    model = mathopt.Model()
    flow, on = pump_variables(model)
    add_pump_rules(model, flow, on, 20)
    print(model.get_num_indicator_constraints(), "indicator constraints")
