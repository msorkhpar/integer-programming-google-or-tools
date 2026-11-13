"""Lesson 14.2.1: the planner after its first request, on GridCap small (a fictional utility).

Runs steps/01 on the small export: one envelope, one yes-or-no per project. Then fills the same
envelope greedily by value per $k, the spreadsheet answer the model replaces.
"""

from export import gridcap_export
from steps import use

raw = gridcap_export("small")
cipt = use(1)
request = cipt.data.load_request(raw)
built = cipt.model.build(request)
print(f"model: {len(built.x)} binary variables, {len(built.rows)} row ({', '.join(built.rows)})")

plan = cipt.solve.solve(request)
print("\n".join(cipt.report.render(request, plan).splitlines()[:2]))



def greedy(projects, envelope):
    """The spreadsheet way: sort by value per $k and take each project that still fits."""
    left, taken = envelope, []
    for p in sorted(projects, key=lambda p: p.value / p.capex, reverse=True):
        if p.capex <= left:
            taken.append(p)
            left -= p.capex
    return taken


print("envelope ($k)   model value   greedy value   greedy short by")
for envelope in (10_000, 15_000, 20_000, 25_000, 30_000, 38_390):
    sized = cipt.data.Request(request.name, envelope, request.projects)
    best = cipt.solve.solve(sized).objective
    quick = sum(p.value for p in greedy(request.projects, envelope))
    print(f"{envelope:>13,}   {best:>11,.0f}   {quick:>12,}   {best - quick:>15,.0f}")
