"""Lesson 4.7.4: five workers, four tasks: LinearSumAssignment needs a square problem.

The data is the OR-Tools assignment example (assignment_mip.py,
https://github.com/google/or-tools/blob/stable/ortools/linear_solver/samples/assignment_mip.py,
Apache-2.0); a dummy task of cost 0 squares it, and a MIP in MathOpt checks the answer.
"""

from ortools.graph.python import linear_sum_assignment
from ortools.math_opt.python import mathopt

COSTS = [[90, 80, 75, 70], [35, 85, 55, 65], [125, 95, 90, 95], [45, 110, 95, 115], [50, 100, 90, 100]]
workers, tasks = len(COSTS), len(COSTS[0])


def lsa(costs):
    a = linear_sum_assignment.SimpleLinearSumAssignment()
    for w, row in enumerate(costs):
        for t, c in enumerate(row):
            a.add_arc_with_cost(w, t, c)
    return a, a.solve()


a, status = lsa(COSTS)
print(f"{workers} workers x {tasks} tasks: {status.name}")

padded = [row + [0] for row in COSTS]                 # task 4 is "no task": cost 0 for everyone
a, status = lsa(padded)
print(f"with a dummy task: {status.name}, cost {a.optimal_cost()}")
for w in range(workers):
    t = a.right_mate(w)
    print(f"  worker {w} -> {'no task' if t == tasks else f'task {t}'}")

model = mathopt.Model(name="assignment")
x = {(w, t): model.add_binary_variable(name=f"x_{w}_{t}") for w in range(workers) for t in range(tasks)}
for w in range(workers):
    model.add_linear_constraint(sum(x[w, t] for t in range(tasks)) <= 1, name=f"worker_{w}")   # at most one task
for t in range(tasks):
    model.add_linear_constraint(sum(x[w, t] for w in range(workers)) == 1, name=f"task_{t}")   # exactly one worker
model.minimize(sum(COSTS[w][t] * x[w, t] for w, t in x))
print(f"MIP: cost {mathopt.solve(model, mathopt.SolverType.HIGHS).objective_value():.0f}")

# Costs are integers in this API.
try:
    linear_sum_assignment.SimpleLinearSumAssignment().add_arc_with_cost(0, 0, 1.5)
except TypeError as error:
    print(f"cost 1.5 -> TypeError: {str(error).splitlines()[0]}")
