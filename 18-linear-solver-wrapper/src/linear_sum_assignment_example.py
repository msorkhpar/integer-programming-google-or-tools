"""Lesson 4.7.4: SimpleLinearSumAssignment on the OR-Tools four-worker example.

Adapted from the OR-Tools example assignment_linear_sum_assignment.py,
https://github.com/google/or-tools/blob/stable/ortools/graph/samples/assignment_linear_sum_assignment.py
(Apache-2.0).
"""

import numpy as np
from ortools.graph.python import linear_sum_assignment

costs = np.array([
    [90, 76, 75, 70],
    [35, 85, 55, 65],
    [125, 95, 90, 105],
    [45, 110, 95, 115],
])
assignment = linear_sum_assignment.SimpleLinearSumAssignment()
# One arc per (worker, task) pair: three parallel arrays, as for the flow solvers.
end_nodes_unraveled, start_nodes_unraveled = np.meshgrid(np.arange(costs.shape[1]), np.arange(costs.shape[0]))
assignment.add_arcs_with_cost(start_nodes_unraveled.ravel(), end_nodes_unraveled.ravel(), costs.ravel())

status = assignment.solve()
if status == assignment.OPTIMAL:
    print(f"total cost = {assignment.optimal_cost()}")
    for worker in range(assignment.num_nodes()):
        print(f"  worker {worker} -> task {assignment.right_mate(worker)}, cost {assignment.assignment_cost(worker)}")
elif status == assignment.INFEASIBLE:
    print("no assignment is possible")
elif status == assignment.POSSIBLE_OVERFLOW:
    print("some costs are too large and may overflow")
