"""Which OR-Tools this is, what it depends on, and the version of each solver inside it (lesson 4.1.2)."""

from __future__ import annotations

import importlib.metadata
import platform

import ortools
from ortools.init.python import init
from ortools.linear_solver import pywraplp

from quiet import captured

print("Python      ", platform.python_version())
print("ortools      ", ortools.__version__)
print("OrToolsVersion", init.OrToolsVersion.version_string())
print("pip requires:", "; ".join(importlib.metadata.requires("ortools")))

print("\nsolver versions, as the linear solver wrapper reports them:")
for solver_id in ("GLOP", "PDLP", "CLP", "CBC", "SCIP", "CP_SAT", "HIGHS"):
    solver = pywraplp.Solver.CreateSolver(solver_id)
    print(f"  {solver_id:<7} {solver.SolverVersion()}")

banner: list[str] = []
with captured(banner):                      # HiGHS writes its banner from C, past Python's print
    solver = pywraplp.Solver.CreateSolver("HIGHS")
    x = solver.IntVar(0, 1, "x")
    solver.Maximize(x)
    solver.Solve()
print("\nwhat HiGHS itself prints when it runs:")
print("  " + next(line for line in banner if line.startswith("Running HiGHS")).split(" (")[0])
