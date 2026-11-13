"""A pumping cost and a valid cut are given (a simpler one than practice 1's); write the loop."""

from __future__ import annotations

from ortools.math_opt.python import mathopt


def pumping_cut(stations: dict, demand: float, limit: float, price: float, plan: dict[str, int], x: dict):
    """The pumping cost of a fixed plan, and a cut that is exact at that plan, in the master's x.

    Not practice 1's answer: the cost comes from filling the need from the cheapest source up, with no
    LP, and the cut is the plain 0/1 one: the cost itself at `plan`, at most 0 at every other plan.
    """
    need = demand + sum(s["refill"] for j, s in stations.items() if plan[j])
    sources = sorted([(s["energy"], s["capacity"]) for j, s in stations.items() if plan[j]] + [(price, limit)])
    cost = 0.0
    for unit, most in sources:
        take = min(most, need)
        cost, need = cost + unit * take, need - take
    differ = sum(1 - x[j] if plan[j] else x[j] for j in stations)     # 0 at `plan`, at least 1 elsewhere
    return cost, cost * (1 - differ)


def benders(stations: dict, demand: float, limit: float, price: float, max_iterations: int = 50):
    """Choose stations by Benders: returns (best total cost, its plan, [(master value, best cost)] per iteration)."""
    # TODO: build the master, then loop: solve it, price its plan with pumping_cut, add the cut.
    return 0.0, {}, []


if __name__ == "__main__":
    stations = {"hill": {"build": 90, "capacity": 60, "energy": 2.0, "refill": 5},
                "lake": {"build": 150, "capacity": 80, "energy": 1.5, "refill": 8}}
    print(benders(stations, 100, 500, 6.0))
