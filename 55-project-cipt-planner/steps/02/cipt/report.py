"""The plan as the planners read it."""

from __future__ import annotations

from .data import Request
from .plan import Plan


def spend_by_year(request: Request, plan: Plan) -> dict[int, int]:
    """What the plan spends in each year, from the funded projects' starts and cost profiles."""
    spend = {y: 0 for y in request.years}
    for pid, start in plan.starts.items():
        for year, amount in request.project(pid).spend(start).items():
            spend[year] += amount
    return spend


def render(request: Request, plan: Plan) -> str:
    lines = [f"{request.name}: {plan.status}"]
    funded = [request.project(pid) for pid in plan.funded]
    capex = sum(p.capex for p in funded)
    value = sum(p.value for p in funded)
    lines.append(f"funded {len(funded)} of {len(request.projects)} projects, "
                 f"capex ${capex:,}k of ${sum(request.budget.values()):,}k, value ${value:,}k")
    for year, spend in spend_by_year(request, plan).items():
        lines.append(f"  {year}  spend ${spend:,}k of ${request.budget[year]:,}k")
    for p in funded:
        lines.append(f"  {p.project_id}  start {plan.starts[p.project_id]}  "
                     f"capex {p.capex:>6,}  value {p.value:>6,}  {p.name}")
    return "\n".join(lines)
