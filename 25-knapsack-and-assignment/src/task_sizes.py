"""Lesson 6.3.2: OR-Tools' assignment with task sizes, a generalized assignment, as a MILP and as its LP.

Ten workers, eight tasks. Each task goes to exactly one worker, and the sizes of the tasks a worker
takes add up to at most 15. The cost depends on the worker and the task; the size only on the task.
"""
# Adapted from the OR-Tools example assignment_task_sizes_mip.py, https://github.com/google/or-tools/blob/stable/ortools/linear_solver/samples/assignment_task_sizes_mip.py

from ortools.math_opt.python import mathopt

from knapsack_models import EXACT, solve_highs

COSTS = [
    [90, 76, 75, 70, 50, 74, 12, 68],
    [35, 85, 55, 65, 48, 101, 70, 83],
    [125, 95, 90, 105, 59, 120, 36, 73],
    [45, 110, 95, 115, 104, 83, 37, 71],
    [60, 105, 80, 75, 59, 62, 93, 88],
    [45, 65, 110, 95, 47, 31, 81, 34],
    [38, 51, 107, 41, 69, 99, 115, 48],
    [47, 85, 57, 71, 92, 77, 109, 36],
    [39, 63, 97, 49, 118, 56, 92, 61],
    [47, 101, 71, 60, 88, 109, 52, 90],
]
TASK_SIZES = [10, 7, 3, 12, 15, 4, 11, 5]
TOTAL_SIZE_MAX = 15


def gap(integer: bool = True):
    model = mathopt.Model(name="assignment_task_sizes")
    workers, tasks = range(len(COSTS)), range(len(TASK_SIZES))
    x = {(w, t): model.add_variable(lb=0, ub=1, is_integer=integer, name=f"x_{w}_{t}") for w in workers for t in tasks}
    for w in workers:                                    # capacity: a knapsack row per worker
        model.add_linear_constraint(sum(TASK_SIZES[t] * x[w, t] for t in tasks) <= TOTAL_SIZE_MAX, name=f"size_{w}")
    for t in tasks:                                      # every task to exactly one worker
        model.add_linear_constraint(sum(x[w, t] for w in workers) == 1, name=f"task_{t}")
    model.minimize(sum(COSTS[w][t] * x[w, t] for w in workers for t in tasks))
    return model, x


if __name__ == "__main__":
    model, x = gap()
    result = solve_highs(model, EXACT)
    pairs = sorted((w, t) for (w, t), v in x.items() if result.variable_values(v) > 0.5)
    print(f"MILP: minimum cost {result.objective_value():.0f}, (worker, task) {pairs}")
    model, x = gap(integer=False)
    lp = mathopt.solve(model, mathopt.SolverType.GLOP)
    split = sorted({t for (w, t), v in x.items() if 1e-6 < lp.variable_values(v) < 1 - 1e-6})
    print(f"LP relaxation: {lp.objective_value():.2f}; tasks split between workers: {split} "
          f"(a vertex may split up to {len(COSTS)}, one per worker)")
