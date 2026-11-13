"""Rounding the five-year model's LP optimum: down is feasible, nearest is not, and a greedy fill adds value."""

from gridcap import generate
from heuristics import Relaxation, broken, fractional, greedy_fill, round_down, round_nearest, rows_of, value
from selection import five_year

model = five_year(generate("medium")).model
m = rows_of(model)
bound, x = Relaxation(model).solve()
print(f"LP bound {bound:,.1f}; fractional variables: "
      + ", ".join(f"{j} = {x[j]:.3f}" for j in fractional(x)))

down = round_down(x)
print(f"round down:    value {value(m, down):,.0f}, breaks {broken(m, down) or 'no row'}")
nearest = round_nearest(x)
print(f"round nearest: value {value(m, nearest):,.0f}, breaks {broken(m, nearest) or 'no row'}")

spend = {j: sum(r.coefs.get(j, 0) for name, r in m.rows.items() if name.startswith("budget")) for j in m.objective}
filled = greedy_fill(m, down, spend)
added = [j for j in filled if filled[j] and not down[j]]
print(f"round down, then greedy fill: adds {', '.join(added)}; value {value(m, filled):,.0f}, "
      f"breaks {broken(m, filled) or 'no row'}")
print(f"  gap to the LP bound: {(bound - value(m, filled)) / value(m, filled):.4%}")
