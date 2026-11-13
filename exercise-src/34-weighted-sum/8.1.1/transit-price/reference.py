from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Upgrade:
    name: str
    cost: int          # $k
    riders: int        # daily riders gained
    co2_kg: int        # kg of CO2 cut per year


def weighted_choice(upgrades: list[Upgrade], budget: int, riders_per_tonne: float) -> set[str]:
    """The upgrades to fund: the most riders plus CO2 cut, priced at `riders_per_tonne`, within budget."""
    model = mathopt.Model(name="depots")
    x = {u.name: model.add_binary_variable(name=f"x_{u.name}") for u in upgrades}
    model.add_linear_constraint(sum(u.cost * x[u.name] for u in upgrades) <= budget, name="budget")
    model.maximize(sum((u.riders + riders_per_tonne * u.co2_kg / 1000) * x[u.name] for u in upgrades))
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return {name for name, var in x.items() if result.variable_values(var) > 0.5}


if __name__ == "__main__":
    depots = [Upgrade("D1", 4, 300, 2000), Upgrade("D2", 3, 100, 9000), Upgrade("D3", 3, 250, 1000)]
    print(sorted(weighted_choice(depots, 6, 50)))
