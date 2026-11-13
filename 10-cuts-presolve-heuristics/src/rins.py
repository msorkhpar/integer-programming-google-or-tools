"""RINS on the five-year model: fix what the incumbent and the LP agree on, solve the small MIP that is left."""

from gridcap import generate
from heuristics import Relaxation, broken, dive, greedy_fill, rins, rins_fixings, round_down, rows_of, value
from selection import five_year

model = five_year(generate("medium")).model
m = rows_of(model)
bound, x = Relaxation(model).solve()
spend = {j: sum(r.coefs.get(j, 0) for name, r in m.rows.items() if name.startswith("budget")) for j in m.objective}
print(f"root LP bound {bound:,.1f}")

starts = {"round down, then fill": greedy_fill(m, round_down(x), spend),
          "the dive": dive(Relaxation(five_year(generate("medium")).model))[0]}
for name, incumbent in starts.items():
    fix = rins_fixings(incumbent, x)
    ones = sum(fix.values())
    print(f"incumbent from {name}: {value(m, incumbent):,.0f}")
    print(f"  it agrees with the LP on {len(fix)} of {len(x)} variables ({ones} at 1, {len(fix) - ones} at 0)")
    plan, free = rins(model, incumbent, x)
    changed = sorted(j for j in plan if plan[j] != incumbent[j])
    print(f"  sub-MIP over the {free} free variables: value {value(m, plan):,.0f}, "
          f"breaks {broken(m, plan) or 'no row'}, changes {len(changed)} decisions")
