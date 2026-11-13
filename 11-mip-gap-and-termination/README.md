# 3.4. MIP Gap and Termination

When a mixed-integer solver stops, and what its answer is worth: the incumbent and the best bound
every run keeps, the absolute and relative gap between them and how each solver divides it, the
rules that stop a run (gap, time, nodes, solutions) and how to read which one fired, and what
"optimal at 0.01%" does and does not promise about a large capital plan. Every example solves
GridCap's project-selection MILP; GridCap, the running dataset, is a fictional utility's portfolio,
not real data.

## Contents

1. [Best bound, incumbent, absolute and relative gap](README_3.4.1.md)
2. [Stopping on gap, time, nodes or solution count](README_3.4.2.md)
3. [What "optimal at 0.01%" means on a $2B portfolio](README_3.4.3.md)
