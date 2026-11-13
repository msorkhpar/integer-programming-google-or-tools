"""Lesson 4.7.1: the OR-Tools linear solver wrapper's first example, as an LP and as a MIP.

Adapted from the OR-Tools examples simple_lp_program.py and simple_mip_program.py,
https://github.com/google/or-tools/tree/stable/ortools/linear_solver/samples (Apache-2.0).
The same model is built three times: continuous variables solved by GLOP, integer variables by
SCIP, and integer variables handed to GLOP.
"""

from ortools.linear_solver import pywraplp


def solve(backend: str, integer: bool) -> None:
    solver = pywraplp.Solver.CreateSolver(backend)        # the solver object also holds the model
    if not solver:
        print(f"{backend} is not available")
        return
    infinity = solver.infinity()
    if integer:
        x = solver.IntVar(0.0, infinity, "x")             # integer, 0 <= x
        y = solver.IntVar(0.0, infinity, "y")
    else:
        x = solver.NumVar(0.0, infinity, "x")             # continuous, 0 <= x
        y = solver.NumVar(0.0, infinity, "y")
    solver.Add(x + 7 * y <= 17.5, "cap")
    solver.Add(x <= 3.5, "x_max")
    solver.Maximize(x + 10 * y)

    status = solver.Solve()
    kind = "integer" if integer else "continuous"
    print(f"{backend}, {kind} x and y: {solver.NumVariables()} variables, {solver.NumConstraints()} constraints, "
          f"status {status}, IsMip() {solver.IsMip()}")
    if status == pywraplp.Solver.OPTIMAL:
        print(f"  objective = {solver.Objective().Value():.2f}, x = {x.solution_value():.2f}, "
              f"y = {y.solution_value():.2f}")
        if integer:
            print(f"  best bound = {solver.Objective().BestBound():.2f}")


solve("GLOP", integer=False)
solve("SCIP", integer=True)
solve("GLOP", integer=True)       # integer variables handed to an LP solver
