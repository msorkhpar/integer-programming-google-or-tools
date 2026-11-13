"""The second-best plan of the base scenario, and how far it is from the best (lesson 9.3.3).

A no-good row cuts off exactly the best plan: sum(chosen) - sum(others) reaches 27, the number of
chosen start variables, only when all of them are 1 and every other is 0, and the row caps it at 26.
The re-solve returns the best plan that differs from the best one.
"""

from gridcap import generate

from diffs import diff_scenarios, show
from explain_model import build, solve

small = generate("small")
best = solve(build(small))

built = build(small)
chosen = [v for (pid, t), v in built.x.items() if best.plan.get(pid) == t]
others = [v for (pid, t), v in built.x.items() if best.plan.get(pid) != t]
built.model.add_linear_constraint(sum(chosen) - sum(others) <= len(chosen) - 1, name="not_best")
second = solve(built)

print(f"best   {best.status}  NPV ${best.npv:,.0f}k")
print(f"second {second.status}  NPV ${second.npv:,.0f}k")
for line in show(diff_scenarios(best, second)):
    print(f"  {line}")
gap = (best.npv - second.npv) / best.npv
print(f"the two differ by {gap:.3%} of the best NPV")
