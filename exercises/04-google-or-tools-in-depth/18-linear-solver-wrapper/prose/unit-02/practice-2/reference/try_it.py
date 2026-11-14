"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.linear_solver import pywraplp

from check import allowed

# Vans v (integer, 0..4) and hours h (0..25): 12 <= 5v + h <= 30, and v + h <= 18.
solver = pywraplp.Solver.CreateSolver("SCIP")
v = solver.IntVar(0, 4, "v")
h = solver.NumVar(0, 25, "h")
band = solver.RowConstraint(12, 30, "band")
band.SetCoefficient(v, 5)
band.SetCoefficient(h, 1)
solver.Add(v + h <= 18, "total")

for plan in ({"v": 2, "h": 8.0}, {"v": 4, "h": 12.0}, {"v": 3, "h": 0.0}, {"v": 1, "h": 3.0}, {"v": 1.5, "h": 9.0}, {"v": 5, "h": 0.0}):
    print(f"plan {plan}:", allowed(solver, plan))
