"""A season of vegetation work for module 16, derived from GridCap small's vegetation projects.

GridCap is a fictional utility's portfolio, and so is everything here. The portfolio gives each
vegetation project its region, its asset (a circuit or a corridor), its crew-months, and the
asset's remaining useful life (RUL) and consequence of failure (CoF). This module turns those into
the data a weekly crew schedule needs, with rules invented for the lessons:

* weeks of work: two weeks per crew-month;
* crews needed at once: 2 for a corridor (widening needs a mower and a climbing crew together),
  1 for a circuit;
* due week: week 6 if the asset's RUL is 2 years or less, week 12 if it is 15 or less, week 20
  otherwise (vegetation grows into the lines of the most worn circuits first);
* risk weight: CoF / 100, read as $k of risk carried for each week the job finishes late;
* outage windows: a circuit *clear* needs the circuit de-energized, which the region's operators
  allow only in the windows of `OUTAGE_WINDOWS` (weeks [a, b): from the start of week a to the
  start of week b).

Weeks are numbered from 0, the first week of the season; a job that starts at week s and lasts d
weeks occupies weeks s, ..., s + d - 1 and ends at s + d.
"""

from __future__ import annotations

from dataclasses import dataclass

from gridcap import generate

HORIZON = 30                    # weeks in the season
CREWS = 3                       # crews in the season's pool
OUTAGE_WINDOWS = {"Ridge": ((0, 8), (14, 24)), "Valley": ((2, 12), (18, 28)),
                  "Coast": ((0, 10), (16, 30)), "Plains": ((4, 14), (20, 30))}


@dataclass(frozen=True)
class Job:
    jid: str            # the GridCap project id
    name: str
    region: str
    kind: str           # "circuit" or "corridor"
    intervention: str   # "trim", "clear" or "widen"
    weeks: int          # weeks of work
    crews: int          # crews it needs at once
    due: int            # the week it should be finished by
    weight: int         # $k of risk per week late

    @property
    def needs_outage(self) -> bool:
        return self.intervention == "clear"


def due_week(rul: int) -> int:
    return 6 if rul <= 2 else 12 if rul <= 15 else 20


def jobs(size: str = "small") -> list[Job]:
    """One job per vegetation project of the GridCap portfolio, in project-id order."""
    portfolio = generate(size)
    found = []
    for p in portfolio.projects:
        if p.program != "vegetation":
            continue
        asset = portfolio.asset(p.asset_id)
        found.append(Job(p.project_id, p.name, p.region, asset.kind, p.intervention,
                         weeks=2 * p.crew_months, crews=2 if asset.kind == "corridor" else 1,
                         due=due_week(asset.rul), weight=asset.cof // 100))
    return found


def by_id(size: str = "small") -> dict[str, Job]:
    return {j.jid: j for j in jobs(size)}


if __name__ == "__main__":
    for j in jobs():
        print(f"{j.jid} {j.region:<6} {j.kind:<8} {j.intervention:<5} weeks {j.weeks}  crews {j.crews}"
              f"  due {j.due:>2}  weight {j.weight:>2}")
