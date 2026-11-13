"""OR-Tools' advanced LP sample: prices, reduced costs and the basis, read after one GLOP solve."""
# Adapted from the OR-Tools example advanced_linear_programming.py, https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/advanced_linear_programming.py

from ortools.math_opt.python import mathopt

model = mathopt.Model(name="advanced-linear-programming-example")
x = [model.add_variable(lb=0.0, name=f"x{j}") for j in range(3)]
rows = [model.add_linear_constraint(10 * x[0] + 4 * x[1] + 5 * x[2] <= 600, name="c1"),
        model.add_linear_constraint(2 * x[0] + 2 * x[1] + 6 * x[2] <= 300, name="c2"),
        model.add_linear_constraint(sum(x) <= 100, name="c3")]
model.maximize(10 * x[0] + 6 * x[1] + 4 * x[2])


def clean(v: float) -> float:
    """0.0 for a solver's -0.0 or a float-noise value, the value itself otherwise."""
    return 0.0 if abs(v) < 1e-9 else v


if __name__ == "__main__":
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        raise RuntimeError(f"model failed to solve to optimality: {result.termination}")
    if not result.has_dual_feasible_solution() or not result.has_basis():
        raise RuntimeError("no dual solution or no basis was returned on optimal")
    print(f"objective {result.objective_value():.4f}")
    for row in rows:
        print(f"  row {row.name}  price {clean(result.dual_values(row)):7.4f}  status {result.constraint_status(row).name}")
    for var in x:
        print(f"  var {var.name}  value {result.variable_values(var):8.4f}  reduced cost {clean(result.reduced_costs(var)):7.4f}"
              f"  status {result.variable_status(var).name}")
