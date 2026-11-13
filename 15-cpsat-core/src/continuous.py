"""Lesson 4.4.4: a continuous amount. CpModel has no such variable; MathOpt's CP-SAT backend takes one.

GridCap is a fictional utility's portfolio. The credit line of lesson 4.4.1 becomes any amount from
$0k to $2,000k, at 0.6 $k of cost per $k borrowed.
"""

from ortools.math_opt.python import mathopt
from ortools.sat.python import cp_model

from gridcap import generate
from cpsat_models import EXACT, solve_highs, mathopt_selection

print("CpModel variable makers:", sorted(n for n in dir(cp_model.CpModel) if n.startswith("new_") and "var" in n
                                         and "interval" not in n and "series" not in n))

small = generate("small")
model, x, k = mathopt_selection(small)
borrow = model.add_variable(lb=0, ub=2_000, name="borrow")       # continuous, $k
model.add_linear_constraint(k == 0)                               # replace the tranches by the amount
budget = next(c for c in model.linear_constraints() if c.name == "budget")
budget.set_coefficient(borrow, -1)
model.objective.set_linear_coefficient(borrow, -0.6)

for solver_type in (mathopt.SolverType.HIGHS, mathopt.SolverType.CP_SAT):
    if solver_type == mathopt.SolverType.HIGHS:
        result = solve_highs(model, EXACT)
    else:
        log = []
        result = mathopt.solve(model, solver_type, params=mathopt.SolveParameters(threads=1),
                               msg_cb=log.extend)
    plan = [i for i, v in x.items() if result.variable_values(v) > 0.5]
    print(f"{solver_type.name:7} {result.termination.reason.name}  objective {result.objective_value():,.1f}"
          f"  borrow ${result.variable_values(borrow):,.1f}k  {len(plan)} projects")
print("from CP-SAT's log:", [line.strip() for line in log if "pure integer" in line])
