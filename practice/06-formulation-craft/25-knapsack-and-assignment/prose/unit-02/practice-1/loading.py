from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Order:
    oid: str
    priority: int
    kg: int
    m3: float
    site: str | None = None      # orders for the same job site travel together


@dataclass(frozen=True)
class Truck:
    tid: str
    max_kg: int
    max_m3: float


def add_loading_rules(model: mathopt.Model, x: dict, orders: list[Order], trucks: list[Truck]) -> None:
    """Each order on at most one truck, every truck within weight and volume, a site's orders together."""
    # TODO: the rows of the four loading rules.
    return None

def build(orders: list[Order], trucks: list[Truck]) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="truck-loading")
    x = {(o.oid, t.tid): model.add_binary_variable(name=f"x_{o.oid}_{t.tid}") for o in orders for t in trucks}
    add_loading_rules(model, x, orders, trucks)
    model.maximize(sum(o.priority * x[o.oid, t.tid] for o in orders for t in trucks))
    return model, x


if __name__ == "__main__":
    model, x = build([Order("O1", 3, 400, 2.0), Order("O2", 5, 900, 1.0, "S1")], [Truck("T1", 1000, 3.0)])
    print(len(list(model.linear_constraints())), "rows")
