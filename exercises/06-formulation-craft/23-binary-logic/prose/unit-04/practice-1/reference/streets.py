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
    extra = []
    for (a, b), cost in detours.items():
        detour = model.add_binary_variable(name=f"detour_{a}_{b}")
        model.add_linear_constraint(detour >= x[a] + x[b] - 1, name=f"detour_{a}_{b}")
        extra.append(cost * detour)
    for k, (corridor, fee) in enumerate(corridor_fees):
        full = model.add_binary_variable(name=f"corridor_{k}")
        model.add_linear_constraint(full >= sum(x[s] for s in corridor) - (len(corridor) - 1),
                                    name=f"corridor_{k}")
        extra.append(fee * full)
    model.add_linear_constraint(sum(s.cost * x[s.sid] for s in streets) + sum(extra) <= budget, name="budget")


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
