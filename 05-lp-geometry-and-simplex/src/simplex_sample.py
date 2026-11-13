"""The 60-line tableau simplex on OR-Tools' three-variable sample LP, beside GLOP's answer."""
# Adapted from the OR-Tools example linear_programming.py, https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/linear_programming.py

from ortools.math_opt.python import mathopt

from simplex import fmt, solve

NAMES = ["x0", "x1", "x2"]
A = [[10, 4, 5],    # c1
     [2, 2, 6],     # c2
     [1, 1, 1]]     # c3
b = [600, 300, 100]
c = [10, 6, 4]


def glop() -> tuple[str, float, list[float]]:
    model = mathopt.Model(name="linear-programming-example")
    x = [model.add_variable(lb=0.0, name=name) for name in NAMES]
    for i, (row, rhs) in enumerate(zip(A, b)):
        model.add_linear_constraint(sum(a * v for a, v in zip(row, x)) <= rhs, name=f"c{i + 1}")
    model.maximize(sum(cj * v for cj, v in zip(c, x)))
    result = mathopt.solve(model, mathopt.SolverType.GLOP)
    return result.termination.reason.name, result.objective_value(), [result.variable_values(v) for v in x]


if __name__ == "__main__":
    result = solve(A, b, c, NAMES + ["s_c1", "s_c2", "s_c3"])
    for entered, left, step, x, value in result.steps:
        print(f"{entered} enters, {left} leaves, step {fmt(step)}: vertex ({', '.join(fmt(v) for v in x)}), value {fmt(value)}")
    print(f"tableau {result.status}: x = ({', '.join(fmt(v) for v in result.x)}), value {fmt(result.value)}")
    status, value, x = glop()
    print(f"GLOP    {status}: x = ({', '.join(f'{v:.4f}' for v in x)}), value {value:.4f}")
