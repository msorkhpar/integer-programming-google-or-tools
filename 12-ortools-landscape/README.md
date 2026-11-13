# 4.1. The OR-Tools Landscape

The map of section 4. OR-Tools is one pip package with several separate solver families inside it:
MathOpt, CP-SAT, the older linear solver wrapper, the routing library, and the graph and knapsack
solvers. This module solves one small GridCap problem in each, measures which solver backends the
course runner's OR-Tools 9.15 actually ships and where each API reports a request it will not carry
out, and ends with a procedure for choosing an API from a problem statement, practiced on ten of
them. Every later module of the section goes deep into one family; this one says which is which.

## Contents

1. [What's in OR-Tools: MathOpt, CP-SAT, linear solver wrapper, routing, graph](README_4.1.1.md)
2. [Versions and the backends that ship with it](README_4.1.2.md)
3. [Choosing an API for a problem](README_4.1.3.md)
