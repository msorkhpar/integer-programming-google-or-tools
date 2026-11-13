"""Lesson 4.7.3: SimpleMaxFlow on the OR-Tools example network.

Adapted from the OR-Tools example simple_max_flow_program.py,
https://github.com/google/or-tools/blob/stable/ortools/graph/samples/simple_max_flow_program.py
(Apache-2.0), itself from Taha, Introduction to Operations Research, example 6.4-2.
"""

import numpy as np
from ortools.graph.python import max_flow

smf = max_flow.SimpleMaxFlow()
start_nodes = np.array([0, 0, 0, 1, 1, 2, 2, 3, 3])
end_nodes = np.array([1, 2, 3, 2, 4, 3, 4, 2, 4])
capacities = np.array([20, 30, 10, 40, 30, 10, 20, 5, 20])
all_arcs = smf.add_arcs_with_capacity(start_nodes, end_nodes, capacities)   # arc indices 0..8

status = smf.solve(0, 4)                  # source 0, sink 4
if status != smf.OPTIMAL:
    raise SystemExit(f"max flow failed: {status}")
print("max flow:", smf.optimal_flow())
for arc, flow, capacity in zip(all_arcs, smf.flows(all_arcs), capacities):
    print(f"  {smf.tail(arc)} -> {smf.head(arc)}  {flow:3} / {capacity:3}")
print("source side of a minimum cut:", sorted(smf.get_source_side_min_cut()))
print("sink side of a minimum cut:  ", sorted(smf.get_sink_side_min_cut()))
