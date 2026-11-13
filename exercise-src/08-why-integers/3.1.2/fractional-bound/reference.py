from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    pid: str
    cost: int
    value: int
    must_do: bool = False


def fractional_bound(projects: list[Project], budget: int) -> float:
    """The LP relaxation's value for one budget row: must-dos, then best value per dollar, then a share."""
    room = budget
    bound = 0.0
    for p in projects:
        if p.must_do:
            room -= p.cost
            bound += p.value
    for p in sorted((p for p in projects if not p.must_do), key=lambda p: p.value / p.cost, reverse=True):
        share = min(1.0, room / p.cost)
        room -= share * p.cost
        bound += share * p.value
        if share < 1:
            break
    return bound


if __name__ == "__main__":
    shops = [Project("A", 30, 60), Project("B", 40, 56), Project("C", 50, 55), Project("D", 20, 18)]
    print(fractional_bound(shops, 120), fractional_bound(shops, 100))
