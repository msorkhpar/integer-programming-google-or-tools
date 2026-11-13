"""Lesson 6.3.2: GridCap small's selection model with four regional crews is a multiple knapsack.

Every funded project is done by exactly one crew, and each crew has a capacity in crew-months.
GridCap and its crews are fictional.
"""

from gridcap import generate
from knapsack_models import CAPACITY, CREWS, EXACT, chosen, selection, solve_highs

# GridCap small: the selection model, and every funded project done by exactly one regional crew.
small = generate("small")
model, y = selection(small)
x = {(p.project_id, k): model.add_binary_variable(name=f"x_{p.project_id}_{k}")
     for p in small.projects for k in CREWS}
for p in small.projects:
    model.add_linear_constraint(sum(x[p.project_id, k] for k in CREWS) == y[p.project_id],
                                name=f"crew_of_{p.project_id}")
for k in CREWS:
    model.add_linear_constraint(sum(p.crew_months * x[p.project_id, k] for p in small.projects) <= CAPACITY[k],
                                name=f"capacity_{k}")
result = solve_highs(model, EXACT)
plan = chosen(y, result)
print(f"GridCap small with crews {', '.join(f'{k} {CAPACITY[k]}' for k in CREWS)}:")
print(f"  {len(plan)} projects, NPV ${result.objective_value():,.0f}k, "
      f"{sum(small.project(i).crew_months for i in plan)} crew-months")
for k in CREWS:
    mine = [i for (i, kk) in chosen(x, result) if kk == k]
    print(f"  {k:<7} {sum(small.project(i).crew_months for i in mine):3} of {CAPACITY[k]}: {' '.join(mine)}")
