"""The plan as the planners read it."""

from __future__ import annotations

from .data import Request
from .plan import Plan


def render(request: Request, plan: Plan) -> str:
    lines = [f"{request.name}: {plan.status}"]
    funded = [request.project(pid) for pid in plan.funded]
    capex = sum(p.capex for p in funded)
    value = sum(p.value for p in funded)
    lines.append(f"funded {len(funded)} of {len(request.projects)} projects, "
                 f"capex ${capex:,}k of ${request.capital_budget:,}k, value ${value:,}k")
    for p in funded:
        lines.append(f"  {p.project_id}  start {plan.starts[p.project_id]}  "
                     f"capex {p.capex:>6,}  value {p.value:>6,}  {p.name}")
    return "\n".join(lines)
