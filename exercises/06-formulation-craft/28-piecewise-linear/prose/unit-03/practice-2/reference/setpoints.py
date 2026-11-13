from __future__ import annotations

import math

from ortools.math_opt.python import mathopt


def add_setpoint(model: mathopt.Model, temp: mathopt.Variable, power: mathopt.Variable,
                 temps: list[float], powers: list[float]) -> None:
    """(temp, power) is one of the listed setpoints, with at most ceil(log2 n) binaries."""
    n = len(temps)
    share = [model.add_variable(lb=0, ub=1, name=f"share_{i}") for i in range(n)]
    model.add_linear_constraint(sum(share) == 1, name="one_setpoint")
    model.add_linear_constraint(temp == sum(t * w for t, w in zip(temps, share)), name="temp")
    model.add_linear_constraint(power == sum(p * w for p, w in zip(powers, share)), name="power")
    for b in range(max(1, math.ceil(math.log2(n)))):
        bit = model.add_binary_variable(name=f"bit_{b}")              # setpoint i has code i
        model.add_linear_constraint(sum(w for i, w in enumerate(share) if i >> b & 1) <= bit, name=f"set_{b}")
        model.add_linear_constraint(sum(w for i, w in enumerate(share) if not i >> b & 1) <= 1 - bit,
                                    name=f"clear_{b}")


def build(temps: list[float], powers: list[float]) -> tuple[mathopt.Model, mathopt.Variable, mathopt.Variable]:
    model = mathopt.Model(name="setpoints")
    temp = model.add_variable(lb=-1e6, ub=1e6, name="temp")
    power = model.add_variable(lb=-1e6, ub=1e6, name="power")
    add_setpoint(model, temp, power, temps, powers)
    return model, temp, power


if __name__ == "__main__":
    model, temp, power = build([70, 75, 80, 85], [420, 360, 310, 300])
    print(sum(v.integer for v in model.variables()), "integer variables")
