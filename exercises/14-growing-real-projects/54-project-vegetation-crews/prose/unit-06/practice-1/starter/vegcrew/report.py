"""The plan as the vegetation manager reads it: one line per crew, one letter per week."""

from __future__ import annotations

from vegcrew.data import Season
from vegcrew.planner import Plan, crew_ids, horizon


def format_plan(season: Season, plan: Plan) -> str:
    lines = [f"season {season.name}: {len(season.circuits)} circuits, budget ${season.budget:,}k, "
             f"crews {season.crews}, weeks {horizon(season)}",
             f"status {plan.status}: {len(plan.trims)} trims, cost ${plan.cost:,}k, "
             f"risk carried ${plan.risk_carried:,}k"]
    for k in crew_ids(season):
        trims = sorted((t for t in plan.trims.values() if t.crew == k), key=lambda t: t.start)
        week = ["."] * horizon(season)
        for first, last in season.crew_off.get(k, ()):
            week[first:last + 1] = "x" * (last - first + 1)
        for t in trims:
            week[t.start:t.end] = t.cid[-1] * (t.end - t.start)
        lines.append(f"  {k} {''.join(week)}  " + " ".join(f"{t.cid}:{t.start}-{t.end - 1}" for t in trims))
    return "\n".join(lines)
