"""OR-Tools' small MIP example, solved as an LP and as a MILP, and its LP answer rounded."""
# Adapted from the OR-Tools example integer_programming.py, https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/integer_programming.py

from ortools.math_opt.python import mathopt


def build(integer: bool) -> tuple[mathopt.Model, mathopt.Variable, mathopt.Variable]:
    model = mathopt.Model(name="mip-example")
    x = model.add_variable(lb=0, ub=3.5, is_integer=integer, name="x")
    y = model.add_variable(lb=0, is_integer=integer, name="y")
    model.add_linear_constraint(x + 7 * y <= 17.5, name="c1")
    model.maximize(x + 10 * y)
    return model, x, y


def allowed(x: float, y: float) -> bool:
    return 0 <= x <= 3.5 and y >= 0 and x + 7 * y <= 17.5


if __name__ == "__main__":
    for integer, solver in ((False, mathopt.SolverType.GLOP), (True, mathopt.SolverType.HIGHS)):
        model, x, y = build(integer)
        result = mathopt.solve(model, solver)
        kind = "MILP" if integer else "LP  "
        print(f"{kind} {solver.name:5} {result.termination.reason.name} value {result.objective_value():.1f}"
              f"  x = {result.variable_values(x):.1f}, y = {result.variable_values(y):.1f}")
    for px, py in ((0, 2), (0, 3)):
        verdict = f"allowed, value {px + 10 * py}" if allowed(px, py) else "breaks c1"
        print(f"rounded ({px}, {py}): {verdict}")
