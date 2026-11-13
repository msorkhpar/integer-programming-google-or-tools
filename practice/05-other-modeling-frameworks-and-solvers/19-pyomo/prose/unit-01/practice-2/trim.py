from __future__ import annotations

from dataclasses import dataclass

import pyomo.environ as pyo


@dataclass(frozen=True)
class Circuit:
    hours: int                  # crew hours to trim it
    risk: float                 # risk removed if it is trimmed
    months: tuple[str, ...]     # the months it may be trimmed in


def trim_plan(circuits: dict[str, Circuit], crew_hours: dict[str, int]) -> tuple[float, dict[str, str]]:
    """The most risk the crews can remove, and the month each trimmed circuit is trimmed in."""
    # TODO: Sets for circuits, months and allowed (circuit, month) pairs; Params; x over the pairs;
    #       the once and crews rows; the objective; solve with appsi_highs and read the plan.
    return 0.0, {}


if __name__ == "__main__":
    lines = {"L1": Circuit(60, 9.0, ("Apr", "May")), "L2": Circuit(50, 7.0, ("Apr",)),
             "L3": Circuit(40, 4.0, ("May", "Jun"))}
    print(trim_plan(lines, {"Apr": 80, "May": 60, "Jun": 30}))
