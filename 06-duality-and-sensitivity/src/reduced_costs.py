"""Lesson 2.3.3: a reduced cost is the price of forcing an idle variable up, and the gap its value must close."""

from budget_lp import build, clean, discount, solve_glop
from gridcap import generate

tiny = generate("tiny")
veg = ("vegetation", 2027)

lp = build(tiny, floor=None)                  # no vegetation floor: vegetation is left idle
result = solve_glop(lp.model)
base = result.objective_value()
print(f"no floor: value {base:,.2f}; {lp.spend[veg].name} = {clean(result.variable_values(lp.spend[veg]), 1)}, "
      f"reduced cost {clean(result.reduced_costs(lp.spend[veg]))}")

for forced in (1, 100):                       # make the plan spend at least this much on it
    lp = build(tiny, floor=None)
    lp.spend[veg].lower_bound = forced
    value = solve_glop(lp.model).objective_value()
    print(f"force {forced:>3}: value {value:,.2f}, change {value - base:,.2f}")

coefficient = lp.model.objective.get_linear_coefficient(lp.spend[veg])
print(f"objective coefficient {coefficient:.4f}")
for raise_by in (0.11, 0.13):                 # just below and just above the reduced cost
    lp = build(tiny, floor=None)
    lp.model.objective.set_linear_coefficient(lp.spend[veg], coefficient + raise_by)
    result = solve_glop(lp.model)
    print(f"coefficient + {raise_by}: {lp.spend[veg].name} = {clean(result.variable_values(lp.spend[veg]), 1)}")
