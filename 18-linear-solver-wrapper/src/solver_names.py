"""Lesson 4.7.1: which back ends the linear solver wrapper (pywraplp) can create in this image.

`CreateSolver` takes a back end's name and returns a solver, or None when that back end is not
built in or has no licence. Nothing is solved here.
"""

from ortools.linear_solver import pywraplp

for name in ("GLOP", "PDLP", "CLP", "SCIP", "CBC", "SAT", "HIGHS", "GUROBI", "XPRESS", "CPLEX", "GLPK"):
    solver = pywraplp.Solver.CreateSolver(name)
    if solver is None:
        print(f"{name:7} None (not available here)")
    else:
        kind = "MIP" if solver.IsMip() else "LP "
        print(f"{name:7} {kind}  {solver.SolverVersion()}")
