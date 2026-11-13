from __future__ import annotations

from ortools.math_opt.python import mathopt


def add_order_rules(model: mathopt.Model, volume: mathopt.Variable, bill: mathopt.Variable,
                    audit: mathopt.Variable, xs: tuple[float, ...], ys: tuple[float, ...],
                    audit_above: float) -> None:
    """The bill on the price curve, and an audit for every order above `audit_above` litres."""
    # TODO: the bill as the curve's value at the volume, and the audit rule.
    return None


def build(xs, ys, audit_above) -> tuple[mathopt.Model, mathopt.Variable, mathopt.Variable, mathopt.Variable]:
    model = mathopt.Model(name="fuel order")
    volume = model.add_variable(lb=0, name="volume")
    bill = model.add_variable(lb=-1e9, ub=1e9, name="bill")
    audit = model.add_binary_variable(name="audit")
    add_order_rules(model, volume, bill, audit, xs, ys, audit_above)
    return model, volume, bill, audit


if __name__ == "__main__":
    model, *_ = build((0, 20_000, 50_000, 80_000), (0, 30_000, 63_000, 87_000), 30_000)
    print(model.get_num_linear_constraints(), "rows")
