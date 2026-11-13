"""Lesson 14.2.6: why a request has no plan, and why a project was deferred, on GridCap small.

GridCap small is a fictional utility's portfolio. The first request cuts the 2030 and 2031 budgets
to $4,000k each; the second asks about projects the NPV plan leaves out, and about P023 when its lag grows.
"""

from export import gridcap_export
from steps import use

raw = gridcap_export("small")
cipt = use(6)

cut = {**raw, "budget": {**raw["budget"], "2030": 4000, "2031": 4000}}
cut_request = cipt.data.load_request(cut)
print(f"budgets cut: {cipt.solve.solve(cut_request).status}, {len(cipt.model.build(cut_request).rows)} rows")
print(cipt.diagnose.why_infeasible(cut_request).message)

request = cipt.data.load_request(raw)
plan = cipt.solve.solve(request)
for pid in ("P030", "P040"):
    d = cipt.diagnose.why_deferred(request, plan, pid)
    print(f"{pid}: funding it costs ${d.npv_cost:,.0f}k of NPV and drops {', '.join(d.displaced)}")

# Engineering asks for three years between P022 and its child P023 instead of one.
longer = {**raw, "projects": [{**r, "parent_lag": 3} if r["id"] == "P023" else r for r in raw["projects"]]}
longer_request = cipt.data.load_request(longer)
d = cipt.diagnose.why_deferred(longer_request, cipt.solve.solve(longer_request), "P023")
print(f"P023 with a three-year lag: cannot be funded. {d.conflict.message}")
