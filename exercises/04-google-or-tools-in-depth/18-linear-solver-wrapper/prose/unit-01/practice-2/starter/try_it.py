"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.linear_solver import pywraplp

from report import crews_model, outcome

# Line crews cover 2 sites, field crews 1; at most `most` of each.
solver, x = crews_model(need=9, most=6)
print("need 9, most 6:", outcome(solver, solver.Solve(), x))
solver, x = crews_model(need=25, most=6)
print("need 25, most 6:", outcome(solver, solver.Solve(), x))
solver, x = crews_model(need=4, most=3)
solver.Solve()
print("need 4, most 3, read as FEASIBLE:", outcome(solver, pywraplp.Solver.FEASIBLE, x))
