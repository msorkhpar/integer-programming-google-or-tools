# 4.7. The Linear Solver Wrapper and Special-Purpose Solvers

Two kinds of OR-Tools code that sit beside MathOpt. The linear solver wrapper, `pywraplp`, is the
older API most OR-Tools guides and much existing code are written in: how to read it, and how to
port a pywraplp model to MathOpt with a test that proves the port gives the same answer. Then the
special-purpose solvers, which need no model at all: `SimpleMaxFlow` and `SimpleMinCostFlow` for
networks, `SimpleLinearSumAssignment` for one-to-one assignment, `KnapsackSolver` for yes/no items
under capacity rows, and bin packing as a MIP with a bound that can make the MIP unnecessary. Each
is checked against a MIP or an LP on GridCap.

## Contents

1. [Reading pywraplp code](README_4.7.1.md)
2. [Migrating a pywraplp model to MathOpt](README_4.7.2.md)
3. [Graph and flow solvers: SimpleMaxFlow and SimpleMinCostFlow](README_4.7.3.md)
4. [Special-purpose solvers: LinearSumAssignment, KnapsackSolver and bin packing](README_4.7.4.md)
