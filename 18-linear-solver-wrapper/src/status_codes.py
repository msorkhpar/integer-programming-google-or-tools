"""Lesson 4.7.1: Solve() returns a plain int, and a solver with no solution still answers value queries.

The model asks for x + y >= 20 with x at most 3 and y at most 10, which no values satisfy.
"""

from ortools.linear_solver import pywraplp

NAMES = {getattr(pywraplp.Solver, n): n for n in
         ("OPTIMAL", "FEASIBLE", "INFEASIBLE", "UNBOUNDED", "ABNORMAL", "MODEL_INVALID", "NOT_SOLVED")}
print("status codes:", ", ".join(f"{code} {name}" for code, name in sorted(NAMES.items())))

solver = pywraplp.Solver.CreateSolver("SCIP")
x = solver.IntVar(0, 3, "x")
y = solver.IntVar(0, 10, "y")
solver.Add(x + y >= 20, "need")
solver.Minimize(x + y)
status = solver.Solve()
print(f"Solve() returned {status!r} ({NAMES[status]})")
print(f"x.solution_value() = {x.solution_value()}, y.solution_value() = {y.solution_value()}, "
      f"Objective().Value() = {solver.Objective().Value()}")
