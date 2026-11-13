from __future__ import annotations

from dataclasses import dataclass

from pulp import PULP_CBC_CMD, LpMaximize, LpProblem, LpVariable, lpSum, value


@dataclass(frozen=True)
class Valve:
    vid: str
    district: str
    risk_cut: float       # expected leak cost avoided a year, $k
    cost: float           # replacement cost, $k
    crew_weeks: int


def plan(valves, budget, crew_weeks, harbor_band, last_year):
    """The best replacement plan as (risk cut, sorted valve ids), or None when no plan exists."""
    z = LpVariable.dicts("z", [v.vid for v in valves], cat="Binary")
    prob = LpProblem("valves", LpMaximize)
    prob += lpSum(v.risk_cut * z[v.vid] for v in valves), "risk_cut"

    prob += lpSum(v.cost * z[v.vid] for v in valves) <= budget, "budget"
    prob += lpSum(v.crew_weeks * z[v.vid] for v in valves), "crew"

    lo, hi = harbor_band
    prob += lo <= lpSum(v.cost * z[v.vid] for v in valves if v.district == "harbor") <= hi, "harbor_band"

    for vid, was_funded in last_year.items():
        if was_funded == 1:
            prob += last_year[vid] == 1, "lock_" + vid

    if prob.solve(PULP_CBC_CMD(msg=0, gapRel=0)):
        return value(prob.objective), sorted(vid for vid in z if value(z[vid]) > 0.5)
    return None


if __name__ == "__main__":
    demo = [Valve("H1", "harbor", 30, 40, 3), Valve("U1", "uptown", 25, 20, 4)]
    print(plan(demo, budget=60, crew_weeks=7, harbor_band=(0, 100), last_year={}))
