from __future__ import annotations

from dataclasses import dataclass

from ortools.math_opt.python import mathopt


@dataclass(frozen=True)
class Pit:
    name: str
    price: float      # $ per ton
    fines: float      # fines content, % of weight
    tons: float       # tons the pit can supply


def mix(pits: list[Pit], tons: float, low: float, high: float):
    """Cheapest blend of `tons` tons whose average fines content lies in [low, high]."""
    # TODO: the model of the statement, a GLOP solve, and the status before any value.
    return "NOT_SOLVED", None, None

if __name__ == "__main__":
    pits = [Pit("A", 12, 4, 500), Pit("B", 9, 9, 600), Pit("C", 7, 14, 400)]
    print(mix(pits, 1000, 6, 10))
