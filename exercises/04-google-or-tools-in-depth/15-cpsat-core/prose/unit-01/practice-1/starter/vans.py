from __future__ import annotations

from dataclasses import dataclass

from ortools.sat.python import cp_model


@dataclass(frozen=True)
class VanType:
    name: str
    capacity: int     # pallets per van
    cost: int         # dollars for the weekend
    available: int    # vans of this type the dealer has
    pack: int         # vans of this type are leased in packs of this many


def build(types: list[VanType], demand: int, budget: int, drivers: int) -> tuple[cp_model.CpModel, dict]:
    """The cheapest fleet that carries the demand, within the budget and the drivers."""
    model = cp_model.CpModel()
    n = {t.name: model.new_int_var(0, 1_000, f"n_{t.name}") for t in types}   # TODO: each type's own domain
    # TODO: the cover, budget and drivers rows, and the objective.
    return model, n


if __name__ == "__main__":
    fleet = [VanType("small", 4, 300, 6, 2), VanType("box", 10, 650, 3, 1)]
    model, n = build(fleet, 30, 3_000, 5)
    solver = cp_model.CpSolver()
    status = solver.solve(model)
    print(solver.status_name(status), {name: solver.value(v) for name, v in n.items()})
