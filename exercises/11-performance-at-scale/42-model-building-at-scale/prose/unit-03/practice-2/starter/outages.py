from __future__ import annotations

from dataclasses import dataclass

WEEKS = 52


@dataclass(frozen=True)
class Outage:
    outage_id: str
    site: str
    start_week: int       # 1 to 52
    weeks: int            # how many weeks the site is out
    crew: int             # crews it needs in every one of those weeks


def active_weeks(o: Outage) -> range:
    return range(o.start_week, o.start_week + o.weeks)


def violations(outages: list[Outage], crews_per_week: int) -> list[str]:
    """One line per broken rule, each starting with the rule's name and a colon."""
    # TODO: one check per rule.
    return []

if __name__ == "__main__":
    plan = [Outage("O1", "Elm", 10, 3, 2), Outage("O2", "Elm", 13, 2, 1), Outage("O3", "Oak", 11, 4, 2)]
    print(violations(plan, crews_per_week=4) or "no violations")
