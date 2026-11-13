# 4.2. MathOpt Core

MathOpt is OR-Tools' solver-independent modeling layer: one model, written once from its
formulation, handed to any solver. This module builds the model piece by piece, reads every part of
the result a solve returns, switches the same model between HiGHS, SCIP, CP-SAT, GLOP, PDLP and
Gurobi, and measures which parameters each solver accepts, including how to read a refusal that
OR-Tools 9.15 hides.

## Contents

1. [Model, variables, constraints, objective](README_4.2.1.md)
2. [Reading `SolveResult`: termination, primal and dual solutions, statistics](README_4.2.2.md)
3. [Switching solvers: HiGHS, SCIP, CP-SAT, GLOP, Gurobi](README_4.2.3.md)
4. [Common vs. solver-specific parameters, and what each solver rejects](README_4.2.4.md)
