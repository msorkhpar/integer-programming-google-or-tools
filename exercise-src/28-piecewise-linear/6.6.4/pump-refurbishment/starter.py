from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt

DEPTHS = (0.0, 0.25, 0.5, 0.75, 1.0)


@dataclass(frozen=True)
class Pump:
    pid: str
    age: float
    beta: float
    eta: float
    cof: float      # $k per failure
    capex: float    # $k for a full refurbishment


def value_points(pump: Pump, horizon: float) -> list[float]:
    """The failure cost avoided over `horizon` years at each depth of DEPTHS, in $k."""
    # TODO: expected failures before and after the refurbishment, times the cost per failure.
    return [0.0] * len(DEPTHS)


def plan(pumps: list[Pump], fund: float, horizon: float) -> tuple[float, dict[str, float]]:
    """The best total value within the fund, and the depth chosen for each pump."""
    # TODO: a depth and a value per pump on its five-point curve, the fund row, and the solve.
    return 0.0, {}


if __name__ == "__main__":
    fleet = [Pump("North", 30, 3.2, 40, 500, 400), Pump("South", 35, 1.4, 45, 900, 500)]
    print([round(v, 1) for v in value_points(fleet[0], 3)])
    print(plan(fleet, 500, 3))
