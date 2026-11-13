from __future__ import annotations

from ortools.math_opt.python import mathopt

Algo = mathopt.LPAlgorithm


def run_method(model: mathopt.Model, solver: mathopt.SolverType, algorithm: mathopt.LPAlgorithm) -> tuple[str, int]:
    """Solve `model` with one solver and one LP algorithm.

    Returns the termination reason's name and the iterations of that algorithm's own kind,
    or ("REFUSED", 0) when the solver does not offer the algorithm.
    """
    try:
        result = mathopt.solve(model, solver, params=mathopt.SolveParameters(lp_algorithm=algorithm))
    except Exception:
        return "REFUSED", 0
    stats = result.solve_stats
    if algorithm in (Algo.PRIMAL_SIMPLEX, Algo.DUAL_SIMPLEX):
        iterations = stats.simplex_iterations
    elif algorithm == Algo.BARRIER:
        iterations = stats.barrier_iterations
    else:
        iterations = stats.first_order_iterations
    return result.termination.reason.name, iterations


if __name__ == "__main__":
    model = mathopt.Model()
    x = [model.add_variable(lb=0, ub=4, name=f"x{i}") for i in range(3)]
    model.add_linear_constraint(x[0] + 2 * x[1] + 3 * x[2] <= 9)
    model.add_linear_constraint(2 * x[0] + x[1] + x[2] <= 7)
    model.maximize(3 * x[0] + 4 * x[1] + 5 * x[2])
    for solver, algorithm in ((mathopt.SolverType.GLOP, Algo.DUAL_SIMPLEX), (mathopt.SolverType.HIGHS, Algo.BARRIER),
                              (mathopt.SolverType.PDLP, Algo.FIRST_ORDER), (mathopt.SolverType.GLOP, Algo.BARRIER)):
        print(solver.name, algorithm.name, run_method(model, solver, algorithm))
