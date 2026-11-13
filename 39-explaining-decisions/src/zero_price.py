"""Binding means zero slack, not a nonzero price (lesson 9.3.1).

The MILP has no prices to read at all. Its LP relaxation has them, and some of its binding rows are
priced at zero.
"""

from collections import Counter

from gridcap import generate

from explain_model import TOL, build, family, slack, solve, solve_highs

small = generate("small")
milp = solve(build(small))
try:
    milp.result.dual_values(milp.built.rows["budget_2030"])
except ValueError as error:
    print(f"MILP dual_values: ValueError: {error}")

relaxed = build(small, integer=False)
result = solve_highs(relaxed.model)
values = result.variable_values()
print(f"LP relaxation: {result.termination.reason.name}, NPV ${result.objective_value():,.1f}k")
print()

kinds = Counter()
for name, row in relaxed.rows.items():
    binding = abs(slack(row, values)) <= TOL
    priced = abs(result.dual_values(row)) > TOL
    kinds[family(name), "binding" if binding else "slack", "priced" if priced else "price 0"] += 1
print("family  slack?    price?   rows")
for (fam, binding, priced), n in sorted(kinds.items()):
    print(f"{fam:7} {binding:8}  {priced:7}  {n:4}")
print()

for name in ("must_P003", "must_P039", "budget_2031"):
    row = relaxed.rows[name]
    print(f"{name:11}  slack {slack(row, values):3.0f}  price {result.dual_values(row) + 0.0:9.4f}")
p003 = small.project("P003")
price_2031 = result.dual_values(relaxed.rows["budget_2031"])
print(f"P003: NPV {p003.npv[2031]}, uses 2031 budget worth {p003.cost_profile[0]} x {price_2031:.4f} = "
      f"{p003.cost_profile[0] * price_2031:.1f}")

statuses = Counter(result.constraint_status(row).name for row in relaxed.rows.values()
                   if abs(slack(row, values)) <= TOL and abs(result.dual_values(row)) <= TOL)
print(f"basis status of the binding rows priced 0: {dict(statuses)}")
