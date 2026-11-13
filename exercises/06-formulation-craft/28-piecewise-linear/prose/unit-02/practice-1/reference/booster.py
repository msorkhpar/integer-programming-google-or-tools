from __future__ import annotations

from ortools.math_opt.python import mathopt


def add_power_curve(model: mathopt.Model, flow: mathopt.Variable, power: mathopt.Variable,
                    xs: tuple[float, ...], ys: tuple[float, ...]) -> None:
    """Rows that make power = f(flow) exactly, for the curve through (xs[j], ys[j])."""
    pick, part_flow, part_power = [], [], []
    for s in range(len(xs) - 1):
        on = model.add_binary_variable(name=f"on_{s}")                  # the pump runs in band s
        q = model.add_variable(lb=0, name=f"q_{s}")                    # the flow, if in band s, else 0
        model.add_linear_constraint(q >= xs[s] * on, name=f"band_lo_{s}")
        model.add_linear_constraint(q <= xs[s + 1] * on, name=f"band_hi_{s}")
        rate = (ys[s + 1] - ys[s]) / (xs[s + 1] - xs[s])
        pick.append(on)
        part_flow.append(q)
        part_power.append((ys[s] - rate * xs[s]) * on + rate * q)
    model.add_linear_constraint(sum(pick) == 1, name="one_band")
    model.add_linear_constraint(flow == sum(part_flow), name="flow_parts")
    model.add_linear_constraint(power == sum(part_power), name="power_parts")


def build(xs: tuple[float, ...], ys: tuple[float, ...]) -> tuple[mathopt.Model, mathopt.Variable, mathopt.Variable]:
    model = mathopt.Model(name="booster")
    flow = model.add_variable(lb=0, name="flow")
    power = model.add_variable(lb=-1e9, ub=1e9, name="power")
    add_power_curve(model, flow, power, xs, ys)
    return model, flow, power


if __name__ == "__main__":
    model, flow, power = build((0, 20, 40, 60, 80), (0, 30, 42, 70, 120))
    print(model.get_num_linear_constraints(), "rows")
