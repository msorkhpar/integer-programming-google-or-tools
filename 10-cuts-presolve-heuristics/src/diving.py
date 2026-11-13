"""Fractional diving on the five-year model: fix, re-solve the LP, repeat until the LP optimum is 0-1."""

from gridcap import generate
from heuristics import Relaxation, broken, dive, rows_of, value
from selection import five_year

model = five_year(generate("medium")).model
m = rows_of(model)
lp = Relaxation(model)
root, _ = lp.solve()
print(f"root LP bound {root:,.1f}")
plan, steps = dive(lp)
for s in steps[:5] + steps[-3:]:
    print(f"  depth {s.depth:3}: {s.variable} at {s.lp_value:.3f}, fix to {s.fixed_to}; LP bound {s.bound:,.1f}")
    if s.depth == 5:
        print("  ...")
flipped = sum(s.fixed_to != int(s.lp_value >= 0.5) for s in steps)
print(f"dive ends after {len(steps)} fixings ({flipped} fixed the other way after an infeasible LP)")
print(f"plan value {value(m, plan):,.0f}, breaks {broken(m, plan) or 'no row'}")
