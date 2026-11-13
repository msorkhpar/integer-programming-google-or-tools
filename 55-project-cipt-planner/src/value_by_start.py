"""Lesson 14.2.4: what the step-03 plan is really worth, and the plans that maximize NPV or risk.

GridCap small is a fictional utility's portfolio. Step 03 valued every project at its
earliest-start NPV whatever year it started; steps/04 reads the NPV of each start year and computes
the risk each start removes from the asset's Weibull curve.
"""

from export import gridcap_export
from steps import use

raw = gridcap_export("small")
npv = {r["id"]: {int(t): v for t, v in r["npv"].items()} for r in raw["projects"]}

old = use(3)
plan = old.solve.solve(old.data.load_request(raw))
real = sum(npv[pid][t] for pid, t in plan.starts.items())
late = {pid: t for pid, t in plan.starts.items() if t > min(npv[pid])}
print(f"step 03 plan: claims ${plan.objective:,.0f}k; its starts are worth ${real:,}k "
      f"({len(late)} projects start after their earliest year)")

new = use(4)
request = new.data.load_request(raw)
p = request.project("P022")
print(f"P022 ({p.asset.asset_id}, age {p.asset.age}, beta {p.asset.weibull_beta}, eta {p.asset.weibull_eta}, "
      f"CoF ${p.asset.cof:,}k), {p.duration} years of work:")
for t in request.starts(p):
    pofs = ", ".join(f"{y}: {new.value.annual_pof(p.asset.weibull_beta, p.asset.weibull_eta, p.asset.age + y - 2027):.3f}"
                     for y in range(t + p.duration, request.years[-1] + 1))
    print(f"  start {t}: NPV ${p.npv[t]:,}k, risk removed ${new.value.risk_reduction(request, p, t):,.1f}k"
          f"  (PoF {pofs or 'no year left in the plan'})")

for goal in ("npv", "risk"):
    goal_request = new.data.load_request({**raw, "objective": goal})
    plan = new.solve.solve(goal_request)
    print(f"maximize {goal:<4}: NPV ${plan.npv:>7,.0f}k, risk removed ${plan.risk:>6,.1f}k, "
          f"{len(plan.starts)} projects funded")
