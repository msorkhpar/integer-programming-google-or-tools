"""The plan as the vegetation manager reads it."""

from __future__ import annotations

from vegcrew.data import WEEKS_PER_MONTH, Season
from vegcrew.planner import Plan


def format_plan(season: Season, plan: Plan) -> str:
    lines = [f"season {season.name}: {len(season.circuits)} circuits, budget ${season.budget:,}k, "
             f"crews {season.crews}, months {season.months}",
             f"status {plan.status}: {len(plan.trims)} trims, cost ${plan.cost:,}k, "
             f"risk removed ${plan.risk_removed:,}k a year"]
    for m in range(1, season.months + 1):
        cids = sorted(cid for cid, t in plan.trims.items() if t.month == m)
        used = sum(season.circuit(cid).weeks for cid in cids)
        work = " ".join(f"{cid}({season.circuit(cid).weeks})" for cid in cids)
        lines.append(f"  month {m}: {used:>2}/{season.crews * WEEKS_PER_MONTH} crew-weeks  {work}".rstrip())
    return "\n".join(lines)
