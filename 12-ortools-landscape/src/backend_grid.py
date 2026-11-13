"""Which solver backends each OR-Tools API accepts in this wheel, asked of each API (lesson 4.1.2)."""

from __future__ import annotations

from ortools.linear_solver import pywraplp
from ortools.linear_solver.python import model_builder
from ortools.math_opt.python import mathopt

print("MathOpt: mathopt.solve(model, SolverType.X)")
for solver in mathopt.SolverType:
    try:
        mathopt.solve(mathopt.Model(), solver)
        verdict = "solves"
    except Exception as error:
        hidden = error.__context__
        reason = hidden.message if hidden is not None else str(error)
        verdict = f"refused: {type(error).__name__}, {reason}"
    print(f"  {solver.name:<9} {verdict}")

print("\nlinear solver wrapper: pywraplp.Solver.CreateSolver(id)")
for solver_id in ("GLOP", "PDLP", "CLP", "HIGHS", "CBC", "SCIP", "CP_SAT", "BOP",
                  "GUROBI", "XPRESS", "CPLEX", "GLPK"):
    solver = pywraplp.Solver.CreateSolver(solver_id)
    if solver is None:
        print(f"  {solver_id:<7} None")
    else:
        print(f"  {solver_id:<7} a solver, {'MIP' if solver.IsMip() else 'LP only'}")

print("\nmodel_builder: model_builder.Solver(name).solver_is_supported()")
names = ("glop", "pdlp", "highs", "scip", "sat", "cbc", "clp", "gurobi", "xpress")
print("  " + ", ".join(f"{n} {model_builder.Solver(n).solver_is_supported()}" for n in names))
