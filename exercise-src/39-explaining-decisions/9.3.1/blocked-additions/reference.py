from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Limit:
    name: str
    use: dict[str, float]       # job -> how much of this limit the job uses
    cap: float


def used(limit: Limit, jobs: set[str]) -> float:
    return sum(limit.use.get(job, 0.0) for job in jobs)


def refusals(limits: list[Limit], plan: set[str], candidates: list[str]) -> dict[str, list[str]]:
    """For each candidate job: the limits that adding it alone to the plan would break, sorted by name."""
    out = {}
    for job in candidates:
        jobs = plan | {job}
        out[job] = sorted(limit.name for limit in limits if used(limit, jobs) - limit.cap > 1e-9)
    return out


def full_but_not_tight(limits: list[Limit], plan: set[str], candidates: list[str]) -> list[str]:
    """Limits with room left at the plan that still refuse at least one candidate, sorted by name."""
    refusing = {name for names in refusals(limits, plan, candidates).values() for name in names}
    return sorted(limit.name for limit in limits
                  if limit.name in refusing and limit.cap - used(limit, plan) > 1e-9)


if __name__ == "__main__":
    fund = Limit("capital_fund", {"roof": 180, "boiler": 220}, 300)
    print(refusals([fund], {"roof"}, ["boiler"]))
