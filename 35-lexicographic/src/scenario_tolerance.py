"""The same 1% and the same $242.6k on three budget scenarios: one follows the scenario, one stays put."""

from dataclasses import replace

from gridcap import generate
from lex_model import build, score
from lexicographic import Level, allowed_loss, solve_levels

small = generate("small")
print("budgets  tolerance  best NPV  allowed  taken  risk removed")
for share in (0.85, 1.0, 1.2):
    scenario = replace(small, budget={y: round(b * share) for y, b in small.budget.items()})
    sm = build(scenario)
    for label, first in (("1%", Level("npv", rel_tol=0.01)), ("$242.6k", Level("npv", abs_tol=242.6))):
        out = solve_levels(sm, [first, Level("risk")])
        best = out.best["npv"]
        print(f"x{share:<6} {label:>9} {best:9,.0f} {allowed_loss(best, first):8,.1f} "
              f"{best - score(sm, out.plan, 'npv'):6,.0f} {score(sm, out.plan, 'risk'):12,.1f}")
