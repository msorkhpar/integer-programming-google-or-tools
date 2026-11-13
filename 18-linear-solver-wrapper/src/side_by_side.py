"""Lesson 4.7.2: one small model in pywraplp and in MathOpt, line for line, with the same answers.

The model is the OR-Tools first example (simple_mip_program.py,
https://github.com/google/or-tools/blob/stable/ortools/linear_solver/samples/simple_mip_program.py,
Apache-2.0) with names on its rows; the LP version adds dual values and reduced costs.
"""

from ortools.linear_solver import pywraplp
from ortools.math_opt.python import mathopt

# ---- pywraplp: the solver is created first, and holds the model
solver = pywraplp.Solver.CreateSolver("SCIP")
x = solver.IntVar(0, solver.infinity(), "x")
y = solver.IntVar(0, solver.infinity(), "y")
cap = solver.Add(x + 7 * y <= 17.5, "cap")
solver.Add(x <= 3.5, "x_max")
solver.Maximize(x + 10 * y)
status = solver.Solve()
if status == pywraplp.Solver.OPTIMAL:
    print(f"pywraplp: objective {solver.Objective().Value():.1f}, x {x.solution_value():.1f}, y {y.solution_value():.1f}")

# ---- MathOpt: the model is built alone; the solver is named at solve time
model = mathopt.Model(name="first")
mx = model.add_integer_variable(lb=0, name="x")
my = model.add_integer_variable(lb=0, name="y")
mcap = model.add_linear_constraint(mx + 7 * my <= 17.5, name="cap")
model.add_linear_constraint(mx <= 3.5, name="x_max")
model.maximize(mx + 10 * my)
result = mathopt.solve(model, mathopt.SolverType.GSCIP)
if result.termination.reason == mathopt.TerminationReason.OPTIMAL:
    print(f"MathOpt:  objective {result.objective_value():.1f}, x {result.variable_values(mx):.1f}, "
          f"y {result.variable_values(my):.1f}")

# ---- the LP relaxation in both, to compare dual values and reduced costs
lp = pywraplp.Solver.CreateSolver("GLOP")
a = lp.NumVar(0, lp.infinity(), "x")
b = lp.NumVar(0, lp.infinity(), "y")
row = lp.Add(a + 7 * b <= 17.5, "cap")
lp.Add(a <= 3.5, "x_max")
lp.Maximize(a + 10 * b)
lp.Solve()
print(f"pywraplp LP: objective {lp.Objective().Value():.2f}, dual(cap) {row.dual_value():.4f}, "
      f"reduced cost(x) {a.reduced_cost():.4f}")

relaxed = mathopt.Model(name="first LP")
ra = relaxed.add_variable(lb=0, name="x")
rb = relaxed.add_variable(lb=0, name="y")
rrow = relaxed.add_linear_constraint(ra + 7 * rb <= 17.5, name="cap")
relaxed.add_linear_constraint(ra <= 3.5, name="x_max")
relaxed.maximize(ra + 10 * rb)
lp_result = mathopt.solve(relaxed, mathopt.SolverType.GLOP)
print(f"MathOpt LP:  objective {lp_result.objective_value():.2f}, dual(cap) {lp_result.dual_values(rrow):.4f}, "
      f"reduced cost(x) {lp_result.reduced_costs(ra):.4f}")

# ---- an infeasible model: pywraplp answers 0.0, MathOpt raises
bad = pywraplp.Solver.CreateSolver("SCIP")
n = bad.IntVar(0, 3, "n")
bad.Add(n >= 5, "need")
print(f"pywraplp infeasible: status {bad.Solve()}, n.solution_value() = {n.solution_value()}")

bad_model = mathopt.Model(name="infeasible")
m = bad_model.add_integer_variable(lb=0, ub=3, name="n")
bad_model.add_linear_constraint(m >= 5, name="need")
bad_result = mathopt.solve(bad_model, mathopt.SolverType.GSCIP)
try:
    bad_result.variable_values(m)
except ValueError as error:
    print(f"MathOpt infeasible: {bad_result.termination.reason.name}, variable_values raised ValueError: {error}")

# ---- default bounds: pywraplp always takes both; MathOpt leaves an omitted bound infinite
defaults = mathopt.Model(name="defaults")
v = defaults.add_variable(name="v")
k = defaults.add_integer_variable(name="k")
print(f"MathOpt bounds left out: add_variable [{v.lower_bound}, {v.upper_bound}], "
      f"add_integer_variable [{k.lower_bound}, {k.upper_bound}]")
