from __future__ import annotations

from ortools.math_opt.python import mathopt


def add_power_curve(model: mathopt.Model, flow: mathopt.Variable, power: mathopt.Variable,
                    xs: tuple[float, ...], ys: tuple[float, ...]) -> None:
    """Rows that make power = f(flow) exactly, for the curve through (xs[j], ys[j])."""
    # TODO: tie each (flow, power) to one segment of the curve.
    return None


def build(xs: tuple[float, ...], ys: tuple[float, ...]) -> tuple[mathopt.Model, mathopt.Variable, mathopt.Variable]:
    model = mathopt.Model(name="booster")
    flow = model.add_variable(lb=0, name="flow")
    power = model.add_variable(lb=-1e9, ub=1e9, name="power")
    add_power_curve(model, flow, power, xs, ys)
    return model, flow, power


if __name__ == "__main__":
    model, flow, power = build((0, 20, 40, 60, 80), (0, 30, 42, 70, 120))
    print(model.get_num_linear_constraints(), "rows")
