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
    # TODO: pay for the must-do projects, then fund the others best value per dollar first,
    # and take the share that fits of the first one that does not fit whole.
    return 0.0


if __name__ == "__main__":
    shops = [Project("A", 30, 60), Project("B", 40, 56), Project("C", 50, 55), Project("D", 20, 18)]
    print(fractional_bound(shops, 120), fractional_bound(shops, 100))
