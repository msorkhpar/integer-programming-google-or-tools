from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    pid: str
    cost: int
    value: int
    must_do: bool = False
    parent: str | None = None
    group: str | None = None


def round_down_and_fill(shares: dict[str, float], projects: list[Project], budget: int) -> set[str]:
    """Keep the projects the LP funded whole, then add the rest best value per dollar while they fit the rules."""
    # TODO: round down (a share within 1e-6 of 1 counts as whole), then walk the other projects
    # best value per dollar first, adding each one that fits the budget and keeps every rule.
    return set()


if __name__ == "__main__":
    pipes = [Project("A", 50, 60, must_do=True), Project("B", 40, 52), Project("H", 30, 24), Project("F", 10, 9)]
    print(round_down_and_fill({"A": 1.0, "B": 0.25, "H": 0.0, "F": 0.0}, pipes, 100))
