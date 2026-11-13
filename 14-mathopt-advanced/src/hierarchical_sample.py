"""Two prioritized objectives on OR-Tools' own small example: which solvers take them, and the result.

Adapted from the OR-Tools example `hierarchical_objectives.py`,
https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/hierarchical_objectives.py
(Apache-2.0). The example solves with Gurobi; the runner has no Gurobi it can load, so the result
below comes from solving the objectives one at a time with HiGHS (in_order.py).
"""

from ortools.math_opt.python import mathopt

from in_order import solve_in_order
from plan_model import refusal, solve

model = mathopt.Model(name="hierarchical")
x = model.add_variable(lb=0, ub=1, name="x")
y = model.add_variable(lb=0, ub=1, name="y")
z = model.add_binary_variable(name="z")
model.add_linear_constraint(x + y + z <= 1.5, name="c")
model.maximize(x + y + 2 * z)                                   # the primary objective, priority 0
aux = model.add_maximization_objective(y, priority=1, name="more_y")

print(f"primary: priority {model.objective.priority}, maximize {model.objective.is_maximize}")
print(f"{aux.name}: priority {aux.priority}, maximize {aux.is_maximize}, id {aux.id}")
print("auxiliary objectives in the model:", model.num_auxiliary_objectives())

for solver in (mathopt.SolverType.HIGHS, mathopt.SolverType.GSCIP, mathopt.SolverType.CP_SAT,
               mathopt.SolverType.GUROBI):
    try:
        solve(model, solver)
    except Exception as error:
        print(f"{solver.name:6} {type(error).__name__:14} reason: {refusal(error)}")

model.delete_auxiliary_objective(aux)                           # the primary objective alone
alone = solve(model, mathopt.SolverType.HIGHS)
print(f"primary only:  objective {alone.objective_value()}  x {alone.variable_values(x)}"
      f"  y {alone.variable_values(y)}  z {alone.variable_values(z)}")

for sense in ("more_y", "less_y"):                                 # the tie broken both ways
    add = model.add_maximization_objective if sense == "more_y" else model.add_minimization_objective
    aux = add(y, priority=1, name=sense)
    reached, values = solve_in_order(model, mathopt.SolverType.HIGHS)
    print(f"in order:      objectives {reached}  x {values['x']}  y {values['y']}  z {values['z']}")
    model.delete_auxiliary_objective(aux)
