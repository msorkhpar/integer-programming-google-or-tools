from __future__ import annotations

import pyomo.environ as pyo


def plan(jobs: dict[str, tuple[float, float]], regular: float,
         hours: list[float], cost: list[float]) -> tuple[float, float, float]:
    """Choose jobs (name -> (hours, value)) to maximize value minus overtime cost.

    Overtime beyond `regular` hours costs the piecewise-linear curve through (hours[k], cost[k]).
    Returns (net value, overtime hours, overtime cost).
    """
    # TODO: x per job; overtime hours and their cost as variables; the time row; a Piecewise for the
    #       cost curve; the objective; solve with appsi_highs.
    return 0.0, 0.0, 0.0


if __name__ == "__main__":
    work = {"A": (30, 900), "B": (20, 500), "C": (25, 400)}
    print(plan(work, 40, [0, 10, 20, 40], [0, 200, 500, 1300]))
