from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass


@dataclass(frozen=True)
class Job:
    years: tuple[int, ...]
    crew: str
    follows: str | None = None
    lag: int = 0


def conflicts(jobs: dict[str, Job], overrides: list[tuple]) -> set[str]:
    """The jobs that take part in a conflict between the overrides and the model's rules."""
    locked = {o[1]: o[2] for o in overrides if o[0] == "lock"}
    banned = {o[1] for o in overrides if o[0] == "ban"}
    found = {j for j, year in locked.items() if year not in jobs[j].years} | (set(locked) & banned)
    by_crew_year = defaultdict(list)
    for j, year in locked.items():
        by_crew_year[jobs[j].crew, year].append(j)
    found |= {j for group in by_crew_year.values() if len(group) > 1 for j in group}
    found |= {j for j, year in locked.items()
              if jobs[j].follows in locked and year < locked[jobs[j].follows] + jobs[j].lag}
    return found


if __name__ == "__main__":
    jobs = {"BRAKES": Job((2027, 2028), "north"), "WHEELS": Job((2028,), "north")}
    print(conflicts(jobs, [("lock", "BRAKES", 2028), ("lock", "WHEELS", 2028)]))
