from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Street:
    sid: str
    cost: int        # $k


def add_traffic_costs(model: mathopt.Model, x: dict, streets: list[Street],
                      detours: dict[tuple[str, str], int], corridor_fees: list[tuple[list[str], int]],
                      budget: int) -> None:
    """Street costs, plus a detour for each adjacent pair rebuilt together, plus each full corridor's fee."""
    # TODO: a variable per detour and per corridor, their rows, and the budget row.
    return None


def build(streets: list[Street], detours: dict[tuple[str, str], int],
          corridor_fees: list[tuple[list[str], int]], budget: int) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="street-works")
    x = {s.sid: model.add_binary_variable(name=f"x_{s.sid}") for s in streets}
    add_traffic_costs(model, x, streets, detours, corridor_fees, budget)
    model.maximize(sum(x.values()))
    return model, x


if __name__ == "__main__":
    streets = [Street("Elm", 100), Street("Oak", 80)]
    model, x = build(streets, {("Elm", "Oak"): 30}, [], 200)
    print(len(list(model.linear_constraints())), "rows")
