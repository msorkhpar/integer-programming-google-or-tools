from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Plan:
    plan_id: str
    name: str
    budget: dict[int, int]                     # year -> $k
    crews: dict[str, list[int]]                # district -> crews available in each month
    parent_id: str | None = None
    created_by: str = ""
    tags: list[str] = field(default_factory=list)


def copy_plan(p: Plan, plan_id: str, name: str, by: str) -> Plan:
    """A new plan with p's inputs, no container shared with p, and a link back to p."""
    # TODO: build the copy.
    return p


if __name__ == "__main__":
    base = Plan("R-1", "base", {2027: 900}, {"north": [3, 3, 4]}, created_by="analyst-a")
    print(copy_plan(base, "R-2", "storm reserve", "analyst-b"))
