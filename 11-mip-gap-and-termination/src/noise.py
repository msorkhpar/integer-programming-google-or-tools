"""NPVs are forecasts. Move each by up to 5% and see how far the best plan moves."""

import random

from gridcap import generate
from selection import build, plan, solve_highs

medium = generate("medium")
sel = build(medium)
planned = solve_highs(sel.model)
chosen = plan(sel, planned)
print(f"plan on the forecast NPVs: {planned.termination.reason.name}, NPV {planned.objective_value():,.0f}, "
      f"gap {planned.best_objective_bound() - planned.objective_value():,.0f}")

print(f"{'seed':>4} {'best plan':>9} {'our plan':>9} {'lost':>5} {'projects changed':>16}")
for seed in (1, 2, 3):
    rng = random.Random(seed)
    actual = {p.project_id: p.value * (1 + rng.uniform(-0.05, 0.05)) for p in medium.projects}
    sel.model.maximize(sum(actual[i] * sel.x[i] for i in sel.x))
    best = solve_highs(sel.model)
    ours = sum(actual[i] for i in chosen)
    print(f"{seed:>4} {best.objective_value():>9,.0f} {ours:>9,.0f} {best.objective_value() - ours:>5,.0f} "
          f"{len(plan(sel, best) ^ chosen):>16}")
