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
    by_id: dict[str, Project] = {}
    for p in projects:
        by_id.setdefault(p.pid, p)
    counts = Counter(p.pid for p in projects)
    problems = [f"duplicate:{pid}" for pid, n in counts.items() if n > 1]
    for p in projects:
        if p.parent is None:
            continue
        if p.parent == p.pid:
            problems.append(f"self-parent:{p.pid}")
        elif p.parent not in by_id:
            problems.append(f"unknown-parent:{p.pid}")
        elif p.group is not None and by_id[p.parent].group == p.group:
            problems.append(f"blocked-child:{p.pid}")
    return problems


if __name__ == "__main__":
    print(link_problems([Project("A", group="g"), Project("B", parent="A", group="g"), Project("C", parent="Z")]))
