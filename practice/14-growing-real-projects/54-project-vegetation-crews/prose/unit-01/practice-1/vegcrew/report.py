"""The plan as the vegetation manager reads it."""

from __future__ import annotations

from vegcrew.data import Season
from vegcrew.planner import Plan


def format_plan(season: Season, plan: Plan) -> str:
    lines = [f"season {season.name}: {len(season.circuits)} circuits, budget ${season.budget:,}k",
             f"status {plan.status}: {len(plan.trims)} trims, cost ${plan.cost:,}k, "
             f"risk removed ${plan.risk_removed:,}k a year"]
    for cid in sorted(plan.trims):
        c = season.circuit(cid)
        lines.append(f"  {cid} {c.region:<5} {c.miles:>3} mi  cost ${c.cost:>4}k  risk ${c.risk:>4}k")
    return "\n".join(lines)
