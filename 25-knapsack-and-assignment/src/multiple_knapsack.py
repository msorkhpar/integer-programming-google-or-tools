"""Lesson 6.3.2: OR-Tools' multiple knapsack example in MathOpt, and the same items under one pooled row.

Adapted from the OR-Tools example `ortools/linear_solver/samples/multiple_knapsack_mip.py`
(Apache-2.0): the same data and rows, written in MathOpt and solved with HiGHS.
"""
# Adapted from the OR-Tools example multiple_knapsack_mip.py, https://github.com/google/or-tools/blob/stable/ortools/linear_solver/samples/multiple_knapsack_mip.py

from ortools.math_opt.python import mathopt

from knapsack_models import solve_highs

weights = [48, 30, 42, 36, 36, 48, 42, 42, 36, 24, 30, 30, 42, 36, 36]
values = [10, 30, 25, 50, 35, 30, 15, 40, 30, 35, 45, 10, 20, 30, 25]
capacities = [100, 100, 100, 100, 100]
items, bins = range(len(weights)), range(len(capacities))

model = mathopt.Model(name="multiple_knapsack")
x = {(i, b): model.add_binary_variable(name=f"x_{i}_{b}") for i in items for b in bins}
for i in items:
    model.add_linear_constraint(sum(x[i, b] for b in bins) <= 1, name=f"once_{i}")       # at most one bin
for b in bins:
    model.add_linear_constraint(sum(weights[i] * x[i, b] for i in items) <= capacities[b], name=f"bin_{b}")
model.maximize(sum(values[i] * x[i, b] for i in items for b in bins))
result = solve_highs(model)
packed = [(i, b) for (i, b), var in x.items() if result.variable_values(var) > 0.5]
print(f"five bins of 100: value {result.objective_value():.0f}, weight {sum(weights[i] for i, _ in packed)}")
for b in bins:
    mine = [i for i, bb in packed if bb == b]
    print(f"  bin {b}: items {mine}, weight {sum(weights[i] for i in mine)}")

pooled = mathopt.Model(name="pooled")
y = [pooled.add_binary_variable(name=f"y_{i}") for i in items]
pooled.add_linear_constraint(sum(weights[i] * y[i] for i in items) <= sum(capacities), name="pooled")
pooled.maximize(sum(values[i] * y[i] for i in items))
result = solve_highs(pooled)
print(f"one pooled row of 500: value {result.objective_value():.0f}, "
      f"weight {sum(weights[i] for i in items if result.variable_values(y[i]) > 0.5)}")
