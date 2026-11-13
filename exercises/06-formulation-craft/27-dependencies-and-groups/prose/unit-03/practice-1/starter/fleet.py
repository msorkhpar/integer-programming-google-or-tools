from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

OPTIONS = ("keep", "refurbish", "diesel", "electric")


@dataclass(frozen=True)
class Bus:
    bid: str
    age: int


def add_fleet_rules(model: mathopt.Model, y: dict, buses: list[Bus], chargers: int, max_age: int) -> None:
    """One option per bus, electric buses within the chargers, no old bus kept."""
    # TODO: your rows.
    return None


def build(buses: list[Bus], chargers: int, max_age: int) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="fleet")
    y = {(b.bid, o): model.add_binary_variable(name=f"y_{b.bid}_{o}") for b in buses for o in OPTIONS}
    add_fleet_rules(model, y, buses, chargers, max_age)
    return model, y


if __name__ == "__main__":
    model, y = build([Bus("B1", 9), Bus("B2", 18)], chargers=1, max_age=15)
    print(model.get_num_linear_constraints(), "rows")
