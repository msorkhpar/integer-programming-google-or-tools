from __future__ import annotations

from collections import Counter
from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    pid: str
    parent: str | None = None
    group: str | None = None


def link_problems(projects: list[Project]) -> list[str]:
    """One string per rule across rows that the list breaks (see the statement's table)."""
    # TODO: check the rules that no single project can break alone.
    return ["not checked yet"]


if __name__ == "__main__":
    print(link_problems([Project("A", group="g"), Project("B", parent="A", group="g"), Project("C", parent="Z")]))
