"""Lesson 3.2.1: the tiny selection model with integrality dropped, solved by GLOP, next to HiGHS's MILP answer."""

from gridcap import generate
from selection import build, solve_lp, solve_milp

tiny = generate("tiny")
print(f"tiny portfolio, capital budget ${tiny.capital_budget:,}k")
for p in tiny.projects:
    rule = "must-do" if p.must_do else f"needs {p.parent}" if p.parent else f"group {p.alt_group}" if p.alt_group else ""
    print(f"  {p.project_id}  capex {p.capex:>5,}  value {p.value:>5,}  {rule}")

lp = solve_lp(build(tiny), fixed={})
print(f"LP relaxation (GLOP): value {lp.value:,.1f}")
for pid, v in lp.x.items():
    print(f"  x_{pid} = {v:.3f}")

milp = solve_milp(build(tiny, integer=True))
print(f"MILP (HiGHS): value {milp.objective_value():,.0f}")
print(f"the LP value is {lp.value - milp.objective_value():,.1f} above the best plan")
