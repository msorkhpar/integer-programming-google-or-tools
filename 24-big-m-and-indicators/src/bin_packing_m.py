"""Lesson 6.2.2: OR-Tools' bin packing example, whose capacity row is a big-M row with M = the capacity.

A bin may hold items only if it is used: load_j <= M * y_j. The OR-Tools example merges that switch
with the capacity, load_j <= 100 * y_j. Written as a separate capacity row and a switch, M can be
the bound rule's value (every item in the bin) or a round number; the MILP answer stays, the LP
bound does not.
"""
# Adapted from the OR-Tools example bin_packing_mip.py, https://github.com/google/or-tools/blob/stable/ortools/linear_solver/samples/bin_packing_mip.py

from ortools.math_opt.python import mathopt

from crew_model import quiet_solve

WEIGHTS = [48, 30, 19, 36, 36, 27, 42, 42, 36, 24, 30]
CAPACITY = 100


def bin_packing(big_m: float | None, *, integer: bool = True) -> mathopt.Model:
    """big_m=None: the example's row load <= CAPACITY * y. Otherwise load <= CAPACITY and load <= big_m * y."""
    model = mathopt.Model(name="bin_packing")
    items = bins = range(len(WEIGHTS))                  # as many bins as items, as in the example
    x = {(i, j): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{i}_{j}") for i in items for j in bins}
    y = {j: model.add_variable(lb=0, ub=1, is_integer=integer, name=f"y_{j}") for j in bins}
    for i in items:
        model.add_linear_constraint(sum(x[i, j] for j in bins) == 1, name=f"item_{i}")
    for j in bins:
        load = sum(WEIGHTS[i] * x[i, j] for i in items)
        if big_m is None:
            model.add_linear_constraint(load <= CAPACITY * y[j], name=f"capacity_{j}")
        else:
            model.add_linear_constraint(load <= CAPACITY, name=f"capacity_{j}")
            model.add_linear_constraint(load <= big_m * y[j], name=f"used_{j}")
    model.minimize(sum(y.values()))
    return model


if __name__ == "__main__":
    print(f"{len(WEIGHTS)} items weighing {sum(WEIGHTS)} in all, bins of {CAPACITY}")
    print(f"{'switch row':28} {'LP bound':>8} {'MILP bins':>9}")
    for name, big_m in [("load <= 100 y (the example)", None), (f"load <= {sum(WEIGHTS)} y (bounds)", sum(WEIGHTS)),
                        ("load <= 1e6 y", 1e6)]:
        lp = quiet_solve(bin_packing(big_m, integer=False), mathopt.SolverType.GLOP)
        milp = quiet_solve(bin_packing(big_m), mathopt.SolverType.HIGHS)
        print(f"{name:28} {lp.objective_value():8.4f} {milp.objective_value():9.0f}")
