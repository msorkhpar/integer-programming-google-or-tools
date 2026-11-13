"""Lesson 4.7.3: SimpleMinCostFlow on the OR-Tools example network.

Adapted from the OR-Tools example simple_min_cost_flow_program.py,
https://github.com/google/or-tools/blob/stable/ortools/graph/samples/simple_min_cost_flow_program.py
(Apache-2.0), itself from Bradley, Hax and Magnanti, Applied Mathematical Programming, figure 8.1.
"""

import numpy as np
from ortools.graph.python import min_cost_flow

smcf = min_cost_flow.SimpleMinCostFlow()
start_nodes = np.array([0, 0, 1, 1, 1, 2, 2, 3, 4])
end_nodes = np.array([1, 2, 2, 3, 4, 3, 4, 4, 2])
capacities = np.array([15, 8, 20, 4, 10, 15, 4, 20, 5])
unit_costs = np.array([4, 4, 2, 2, 6, 1, 3, 2, 3])
supplies = [20, 0, 0, -5, -15]                     # + supplies, - demands; they sum to 0

all_arcs = smcf.add_arcs_with_capacity_and_unit_cost(start_nodes, end_nodes, capacities, unit_costs)
smcf.set_nodes_supplies(np.arange(0, len(supplies)), supplies)

status = smcf.solve()
if status != smcf.OPTIMAL:
    raise SystemExit(f"min cost flow failed: {status}")
print("minimum cost:", smcf.optimal_cost())
for arc, flow, cost in zip(all_arcs, smcf.flows(all_arcs), unit_costs):
    print(f"  {smcf.tail(arc)} -> {smcf.head(arc)}  {flow:3} / {smcf.capacity(arc):3}  cost {flow * cost}")
