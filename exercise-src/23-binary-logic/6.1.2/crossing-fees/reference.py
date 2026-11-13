from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Upgrade:
    pid: str
    cost: int        # $k


def add_fee_rules(model: mathopt.Model, x: dict, projects: list[Upgrade],
                  permits: dict[str, tuple[int, list[str]]], bundles: list[tuple[str, str, int]],
                  budget: int) -> None:
    """Costs plus each needed permit's fee, once, minus each complete bundle's discount, within budget."""
    charged = []
    for name, (fee, members) in permits.items():
        paid = model.add_binary_variable(name=f"permit_{name}")
        for i in members:
            model.add_linear_constraint(paid >= x[i], name=f"permit_{name}_{i}")
        charged.append(fee * paid)
    for tower, backhaul, discount in bundles:
        both = model.add_binary_variable(name=f"bundle_{tower}_{backhaul}")
        model.add_linear_constraint(both <= x[tower], name=f"bundle_{tower}_{backhaul}_t")
        model.add_linear_constraint(both <= x[backhaul], name=f"bundle_{tower}_{backhaul}_b")
        charged.append(-discount * both)
    model.add_linear_constraint(sum(p.cost * x[p.pid] for p in projects) + sum(charged) <= budget,
                                name="budget")


def build(projects: list[Upgrade], permits: dict[str, tuple[int, list[str]]],
          bundles: list[tuple[str, str, int]], budget: int) -> tuple[mathopt.Model, dict]:
    model = mathopt.Model(name="tower-upgrades")
    x = {p.pid: model.add_binary_variable(name=f"x_{p.pid}") for p in projects}
    add_fee_rules(model, x, projects, permits, bundles, budget)
    model.maximize(sum(x.values()))
    return model, x


if __name__ == "__main__":
    upgrades = [Upgrade("T1", 100), Upgrade("B1", 60), Upgrade("C1", 50)]
    model, x = build(upgrades, {"river": (25, ["C1"])}, [("T1", "B1", 40)], 200)
    print(len(list(model.linear_constraints())), "rows")
