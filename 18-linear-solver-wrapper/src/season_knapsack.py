"""Lesson 4.7.4: the most valuable work one 12-month crew season can do, by KnapsackSolver and by a MIP.

Items are GridCap small's distribution and vegetation projects, weighed in crew-months and valued
at their NPV ($k). GridCap is a fictional utility's portfolio; the season is invented.
"""

from ortools.algorithms.python import knapsack_solver
from ortools.math_opt.python import mathopt

from gridcap import generate

SEASON = 12

small = generate("small")
work = [p for p in small.projects if p.program in ("distribution", "vegetation")]
values = [p.value for p in work]                       # $k, whole numbers
weights = [[p.crew_months for p in work]]              # one row: a list holding one list
capacities = [SEASON]

solver = knapsack_solver.KnapsackSolver(knapsack_solver.SolverType.KNAPSACK_DYNAMIC_PROGRAMMING_SOLVER, "season")
solver.init(values, weights, capacities)
best = solver.solve()
picked = [work[i].project_id for i in range(len(work)) if solver.best_solution_contains(i)]
print(f"KnapsackSolver (dynamic programming): ${best:,}k from {' '.join(picked)}, "
      f"{sum(small.project(pid).crew_months for pid in picked)} crew-months")

model = mathopt.Model(name="season")
x = [model.add_binary_variable(name=f"x_{p.project_id}") for p in work]
model.add_linear_constraint(sum(p.crew_months * xi for p, xi in zip(work, x)) <= SEASON, name="season")
model.maximize(sum(p.value * xi for p, xi in zip(work, x)))
result = mathopt.solve(model, mathopt.SolverType.CP_SAT)
print(f"MIP check (CP-SAT): ${result.objective_value():,.0f}k")
