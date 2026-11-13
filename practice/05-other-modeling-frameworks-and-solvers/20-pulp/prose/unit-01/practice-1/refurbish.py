from __future__ import annotations

from dataclasses import dataclass

import pulp


@dataclass(frozen=True)
class Station:
    sid: str
    savings: float        # energy saved per year after the refurbishment, $k
    cost: float           # cost of the refurbishment, $k
    crew_days: int        # crew-days the refurbishment takes
    must: bool = False    # required by the regulator this year


def build(stations: list[Station], budget: float, crew_days: int,
          bypass_pairs: list[tuple[str, str]]) -> tuple[pulp.LpProblem, dict[str, pulp.LpVariable]]:
    """The refurbishment model, with one named row per rule."""
    prob = pulp.LpProblem("pump_refurbishment", pulp.LpMaximize)
    y = {s.sid: prob.add_variable(f"y_{s.sid}", 0, 1, cat=pulp.LpBinary) for s in stations}
    prob += pulp.lpSum(s.savings * y[s.sid] for s in stations), "savings"
    # TODO: add the budget, crew, bypass and must rows of the formulation, each with its name.
    return prob, y


def refurbish(stations: list[Station], budget: float, crew_days: int,
              bypass_pairs: list[tuple[str, str]]) -> tuple[float, list[str]]:
    """Solve with CBC at a gap of 0: the yearly savings and the stations to refurbish, sorted."""
    prob, y = build(stations, budget, crew_days, bypass_pairs)
    prob.solve(pulp.PULP_CBC_CMD(msg=False, gapRel=0))
    return pulp.value(prob.objective), sorted(sid for sid, v in y.items() if v.varValue > 0.5)


if __name__ == "__main__":
    demo = [Station("N1", 20, 30, 4), Station("N2", 15, 20, 3, must=True), Station("N3", 18, 25, 5)]
    print(refurbish(demo, budget=50, crew_days=8, bypass_pairs=[("N1", "N3")]))
