from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def add_setpoint(model: mathopt.Model, temp: mathopt.Variable, power: mathopt.Variable,
                 temps: list[float], powers: list[float]) -> None:
    """(temp, power) is one of the listed setpoints, with at most ceil(log2 n) binaries."""
    # TODO: a weight per setpoint, a code per setpoint, and the bit rows.
    return None


def build(temps: list[float], powers: list[float]) -> tuple[mathopt.Model, mathopt.Variable, mathopt.Variable]:
    model = mathopt.Model(name="setpoints")
    temp = model.add_variable(lb=-1e6, ub=1e6, name="temp")
    power = model.add_variable(lb=-1e6, ub=1e6, name="power")
    add_setpoint(model, temp, power, temps, powers)
    return model, temp, power


if __name__ == "__main__":
    model, temp, power = build([70, 75, 80, 85], [420, 360, 310, 300])
    print(sum(v.integer for v in model.variables()), "integer variables")
