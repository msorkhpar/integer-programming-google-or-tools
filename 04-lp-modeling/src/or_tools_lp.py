"""OR-Tools' own first MathOpt LP, read the way lesson 2.1.1 reads the split: status, values, rows."""
# Adapted from the OR-Tools example linear_programming.py, https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/linear_programming.py

from ortools.math_opt.python import mathopt

from program_split import activity


def build() -> tuple[mathopt.Model, list[mathopt.Variable], list[mathopt.LinearConstraint]]:
    model = mathopt.Model(name="linear-programming-example")
    x = [model.add_variable(lb=0.0, name=f"x{j}") for j in range(3)]
    rows = [model.add_linear_constraint(10 * x[0] + 4 * x[1] + 5 * x[2] <= 600, name="c1"),
            model.add_linear_constraint(2 * x[0] + 2 * x[1] + 6 * x[2] <= 300, name="c2"),
            model.add_linear_constraint(sum(x) <= 100, name="c3")]
    model.maximize(10 * x[0] + 6 * x[1] + 4 * x[2])
    return model, x, rows


if __name__ == "__main__":
    model, x, rows = build()
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        raise RuntimeError(f"model failed to solve to optimality: {result.termination}")
    print("status", result.termination.reason.name, f" objective {result.objective_value():.2f}")
    print("  " + "  ".join(f"{v.name} = {result.variable_values(v):.2f}" for v in x))
    for row in rows:
        room = row.upper_bound - activity(row, result)
        print(f"  {row.name}  activity {activity(row, result):6.2f}  <= {row.upper_bound:3.0f}  "
              + ("full" if abs(room) <= 1e-6 else f"room {room:.2f}"))
