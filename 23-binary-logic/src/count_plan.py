"""Lesson 6.1.1: sums of binaries count, and weighted sums total, read on GridCap small's best plan.

GridCap is a fictional utility's portfolio.
"""

from ortools.math_opt.python import mathopt

from gridcap import PROGRAMS, REGIONS, generate
from selection_model import EXACT, build, funded, ids, solve_highs

small = generate("small")
sel = build(small)
result = solve_highs(sel.model, EXACT)
plan = funded(sel, result)
print(f"GridCap small: the best plan funds {len(plan)} of {len(small.projects)} projects, "
      f"NPV ${result.objective_value():,.0f}k")

x = sel.x
count_program = {g: sum(x[i] for i in ids(small, program=g)) for g in PROGRAMS}
count_region = {r: sum(x[i] for i in ids(small, region=r)) for r in REGIONS}
capex = sum(p.capex * x[p.project_id] for p in small.projects)
crew = sum(p.crew_months * x[p.project_id] for p in small.projects)

values = {v: result.variable_values(v) for v in x.values()}
print("count by program:", ", ".join(
    f"{g} {mathopt.evaluate_expression(e, values):.0f}" for g, e in count_program.items()))
print("count by region: ", ", ".join(
    f"{r} {mathopt.evaluate_expression(e, values):.0f}" for r, e in count_region.items()))
print(f"capex ${mathopt.evaluate_expression(capex, values):,.0f}k of ${small.capital_budget:,}k; "
      f"crew-months {mathopt.evaluate_expression(crew, values):.0f}")
print("candidates by program:", ", ".join(f"{g} {len(ids(small, program=g))}" for g in PROGRAMS))
