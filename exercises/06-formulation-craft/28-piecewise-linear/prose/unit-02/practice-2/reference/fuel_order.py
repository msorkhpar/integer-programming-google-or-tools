from __future__ import annotations

from ortools.math_opt.python import mathopt


def add_order_rules(model: mathopt.Model, volume: mathopt.Variable, bill: mathopt.Variable,
                    audit: mathopt.Variable, xs: tuple[float, ...], ys: tuple[float, ...],
                    audit_above: float) -> None:
    """The bill on the price curve, and an audit for every order above `audit_above` litres."""
    def price(v: float) -> float:
        for k in range(len(xs) - 1):
            if xs[k] <= v <= xs[k + 1]:
                return ys[k] + (ys[k + 1] - ys[k]) * (v - xs[k]) / (xs[k + 1] - xs[k])
        raise ValueError(v)

    points = sorted(set(xs) | {audit_above})          # the audit volume becomes a breakpoint
    weight = {}
    for j, at in enumerate(points):
        weight[j] = model.add_variable(lb=0, ub=1, name=f"w_{j}")
    band = {k: model.add_binary_variable(name=f"band_{k}") for k in range(len(points) - 1)}
    model.add_linear_constraint(sum(weight.values()) == 1, name="weights")
    model.add_linear_constraint(sum(band.values()) == 1, name="one_band")
    for j in weight:
        near = [band[k] for k in band if k in (j - 1, j)]
        model.add_linear_constraint(weight[j] <= sum(near), name=f"near_{j}")
    model.add_linear_constraint(volume == sum(at * weight[j] for j, at in enumerate(points)), name="volume")
    model.add_linear_constraint(bill == sum(price(at) * weight[j] for j, at in enumerate(points)), name="bill")
    for k, start in enumerate(points[:-1]):
        if start >= audit_above:
            model.add_linear_constraint(audit >= band[k], name=f"audit_{k}")


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
