"""GridCap small: the plan that removes the most risk next to the plan with the most NPV."""

from asset_curves import eta_from_rul
from dataclasses import replace
from gridcap import generate
from risk_model import build, plan_of, risk_coefficients, solve_highs

small = generate("small")
rr = risk_coefficients(small)
npv = {(p.project_id, t): p.npv[t] for p in small.projects for t in p.starts()}

plans = {}
for name, objective in (("max NPV", npv), ("max risk reduction", rr)):
    sm = build(small, objective)
    result = solve_highs(sm.model)
    plans[name] = plan = plan_of(sm, result)
    print(f"{name:18}: {len(plan)} projects, NPV ${sum(npv[k] for k in plan.items()):,}k, "
          f"risk removed ${sum(rr[k] for k in plan.items()):,.0f}k ({result.termination.reason.name})")
both = set(plans["max NPV"]) & set(plans["max risk reduction"])
print(f"projects in both plans: {len(both)}")
for name, plan in plans.items():
    slack = {r: sum(small.project(pid).capex for pid in plan if small.project(pid).region == r) - floor
             for r, floor in small.region_floor.items()}
    print(f"{name}: capex funded above each region floor ($k): "
          + ", ".join(f"{r} {v:,}" for r, v in slack.items()) + f"; every floor met: {min(slack.values()) >= 0}")

from_rul = risk_coefficients(small, eta_of=lambda a: replace(a, weibull_eta=eta_from_rul(a.age, a.rul, a.weibull_beta)))
sm = build(small, from_rul)
plan = plan_of(sm, solve_highs(sm.model))
moved = set(plan) ^ set(plans["max risk reduction"])
print(f"with eta calibrated to each RUL: {len(plan)} projects, risk removed by the curve's own measure "
      f"${sum(rr[k] for k in plan.items()):,.0f}k; projects that differ: {', '.join(sorted(moved))}")
