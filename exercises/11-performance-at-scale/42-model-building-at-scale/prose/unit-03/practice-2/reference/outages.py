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
    out = []
    ids = [o.outage_id for o in outages]
    out += [f"unique ids: {i}" for i in sorted({i for i in ids if ids.count(i) > 1})]
    for o in outages:
        if o.weeks < 1 or o.start_week < 1 or o.start_week + o.weeks - 1 > WEEKS:
            out.append(f"inside the year: {o.outage_id}")
    for a in outages:
        for b in outages:
            if a.outage_id < b.outage_id and a.site == b.site and set(active_weeks(a)) & set(active_weeks(b)):
                out.append(f"one outage per site: {a.outage_id} and {b.outage_id}")
    load = {}
    for o in outages:
        for week in active_weeks(o):
            load[week] = load.get(week, 0) + o.crew
    out += [f"crews suffice: week {w} needs {n}" for w, n in sorted(load.items()) if n > crews_per_week]
    return out


if __name__ == "__main__":
    plan = [Outage("O1", "Elm", 10, 3, 2), Outage("O2", "Elm", 13, 2, 1), Outage("O3", "Oak", 11, 4, 2)]
    print(violations(plan, crews_per_week=4) or "no violations")
