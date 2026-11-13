"""The dual pair of OR-Tools' LP guide: a minimization whose <= row gets a price <= 0, read two ways."""
# Adapted from the OR-Tools example of a primal-dual pair in "Advanced LP Solving", https://developers.google.com/optimization/lp/lp_advanced

from ortools.linear_solver import pywraplp
from ortools.math_opt.python import mathopt


def with_mathopt() -> tuple[float, list[float], float, list[float]]:
    model = mathopt.Model(name="dual-example")
    x1 = model.add_variable(lb=0, name="x1")
    x2 = model.add_variable(lb=0, name="x2")
    row = model.add_linear_constraint(x1 + x2 <= 1, name="c")
    model.minimize(-2 * x1 - x2)
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        raise SystemExit(result.termination.reason.name)
    return (result.objective_value(), result.variable_values([x1, x2]),
            result.dual_values(row), result.reduced_costs([x1, x2]))


def with_pywraplp() -> tuple[float, float, list[float]]:
    solver = pywraplp.Solver.CreateSolver("GLOP")
    x1 = solver.NumVar(0, solver.infinity(), "x1")
    x2 = solver.NumVar(0, solver.infinity(), "x2")
    row = solver.Add(x1 + x2 <= 1)
    solver.Minimize(-2 * x1 - x2)
    if solver.Solve() != pywraplp.Solver.OPTIMAL:
        raise SystemExit("not optimal")
    return solver.Objective().Value(), row.dual_value(), [x1.reduced_cost(), x2.reduced_cost()]


if __name__ == "__main__":
    value, x, price, reduced = with_mathopt()
    print(f"min -2 x1 - x2, x1 + x2 <= 1: value {value:g} at (x1, x2) = ({x[0]:g}, {x[1]:g})")
    print(f"MathOpt  dual_values  {price:g}   reduced_costs ({reduced[0]:g}, {reduced[1]:g})")
    value, price, reduced = with_pywraplp()
    print(f"pywraplp dual_value   {price:g}   reduced_cost  ({reduced[0]:g}, {reduced[1]:g})")
