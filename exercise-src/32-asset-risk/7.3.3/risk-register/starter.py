import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Valve:
    valve_id: str
    age: float
    beta: float
    eta: float
    cof: float


def survival(t: float, beta: float, eta: float) -> float:
    return math.exp(-((t / eta) ** beta))


def risk(v: Valve) -> float:
    """Expected failure cost of the valve in the coming year, $k."""
    # TODO: the chance a working valve of this age fails within the year, times the cost.
    return 0.0


def rank_by_risk(valves: list[Valve]) -> list[str]:
    """Valve ids, highest risk first."""
    # TODO: sort by risk.
    return [v.valve_id for v in valves]


if __name__ == "__main__":
    print(rank_by_risk([Valve("V1", 40, 3.0, 45, 800), Valve("V2", 10, 3.0, 45, 2_000)]))
