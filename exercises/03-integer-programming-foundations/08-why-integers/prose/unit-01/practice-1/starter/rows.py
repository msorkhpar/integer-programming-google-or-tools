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


def broken_rows(plan: set[str], projects: list[Project], budget: int) -> set[str]:
    """The labels of the rows a 0/1 plan breaks: budget, must_<pid>, parent_<pid>, alt_<group>."""
    # TODO: check each row of the model and collect the label of every row the plan breaks.
    return set()


if __name__ == "__main__":
    mains = [Project("M1", 40, 55, must_do=True), Project("M2", 30, 42), Project("M3", 30, 36, parent="M2"),
             Project("M4", 20, 26, group="G1"), Project("M5", 15, 24, group="G1")]
    print(broken_rows({"M1", "M2", "M3", "M4", "M5"}, mains, 100))
    print(broken_rows({"M2", "M3"}, mains, 100))
