"""Every rule of the request, checked on a finished plan in plain Python, apart from the model."""

from __future__ import annotations

from .fleet import FIRST_YEAR, KINDS, Transformer
from .report import outages, spend_by_year
from .request import Request


def violations(fleet: list[Transformer], request: Request, replace: dict[str, int]) -> list[str]:
    """One line per broken rule; an empty list means the plan keeps every rule."""
    by_id = {t.tid: t for t in fleet}
    found = []
    for tid, y in sorted(replace.items()):
        if y not in request.plan_years():
            found.append(f"{tid}: {y} is outside the plan")
        if by_id[tid].age < request.min_age:
            found.append(f"{tid}: younger than {request.min_age}, not a candidate")
    for y, spend in spend_by_year(fleet, replace, request.outage_cost).items():
        if spend > request.budget:
            found.append(f"budget {y}: {spend} > {request.budget}")
    if request.outages is not None:
        taken: dict[tuple[str, int], int] = {}
        region = {t.substation: t.region for t in fleet}
        for s, y in outages(fleet, replace):
            taken[region[s], y] = taken.get((region[s], y), 0) + 1
        found += [f"outages {r} {y}: {n} > {request.outages}" for (r, y), n in sorted(taken.items())
                  if n > request.outages]
    if request.crew_weeks is not None:
        weeks: dict[tuple[str, int], int] = {}
        for tid, y in replace.items():
            t = by_id[tid]
            weeks[t.region, y] = weeks.get((t.region, y), 0) + KINDS[t.kind].crew_weeks
        found += [f"crews {r} {y}: {w} > {request.crew_weeks}" for (r, y), w in sorted(weeks.items())
                  if w > request.crew_weeks]
    if request.lead_times:
        for kind, k in KINDS.items():
            early = sum(1 for tid, y in replace.items()
                        if by_id[tid].kind == kind and y < FIRST_YEAR + k.lead_years)
            if early > request.spares.get(kind, 0):
                found.append(f"spares {kind}: {early} > {request.spares.get(kind, 0)}")
    return found
