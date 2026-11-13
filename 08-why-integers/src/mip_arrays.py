"""OR-Tools' five-variable MIP example: its LP answer rounded three ways, and the MILP's answer."""
# Adapted from the OR-Tools example mip_var_array.py, https://github.com/google/or-tools/blob/stable/ortools/linear_solver/samples/mip_var_array.py

import math

from ortools.math_opt.python import mathopt

from selection import solve_highs

ROWS = [[5, 7, 9, 2, 1], [18, 4, -9, 10, 12], [4, 7, 3, 8, 5], [5, 13, 16, 3, -7]]
RHS = [250, 285, 211, 315]
OBJ = [7, 8, 2, 9, 6]


def build(integer: bool) -> tuple[mathopt.Model, list[mathopt.Variable]]:
    model = mathopt.Model(name="mip-var-array")
    x = [model.add_variable(lb=0, is_integer=integer, name=f"x{j}") for j in range(len(OBJ))]
    for i, (row, rhs) in enumerate(zip(ROWS, RHS)):
        model.add_linear_constraint(sum(a * v for a, v in zip(row, x)) <= rhs, name=f"c{i}")
    model.maximize(sum(c * v for c, v in zip(OBJ, x)))
    return model, x


def broken(point: list[int]) -> list[str]:
    return [f"c{i}" for i, (row, rhs) in enumerate(zip(ROWS, RHS)) if sum(a * v for a, v in zip(row, point)) > rhs]


if __name__ == "__main__":
    model, x = build(integer=False)
    lp = mathopt.solve(model, mathopt.SolverType.GLOP)
    point = [lp.variable_values(v) for v in x]
    print(f"LP (GLOP): value {lp.objective_value():.2f} at ({', '.join(f'{v:.3f}' for v in point)})")
    for name, rule in (("down", math.floor), ("nearest", lambda v: math.floor(v + 0.5)), ("up", math.ceil)):
        whole = [rule(v) for v in point]
        value = sum(c * v for c, v in zip(OBJ, whole))
        print(f"  round {name:<7} ({', '.join(map(str, whole))}): value {value}, breaks {broken(whole)}")
    change = ROWS[3][4] * (math.floor(point[4]) - point[4])
    print(f"  rounding x4 down changes c3 by {change:+.2f}: its coefficient there is {ROWS[3][4]}")
    model, x = build(integer=True)
    milp = solve_highs(model)
    best = [round(milp.variable_values(v)) for v in x]
    print(f"MILP (HiGHS): {milp.termination.reason.name}, value {milp.objective_value():.0f} at "
          f"({', '.join(map(str, best))})")
    print("nodes to prove the optimum:")
    print(f"  HiGHS {milp.solve_stats.node_count}, "
          f"SCIP {mathopt.solve(build(integer=True)[0], mathopt.SolverType.GSCIP).solve_stats.node_count}")
