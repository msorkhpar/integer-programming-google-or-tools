"""Column generation for GridCap's vegetation crew-days, adapted from the OR-Tools MathOpt example
`cutting_stock.py` (https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/cutting_stock.py).

The sample cuts boards into pieces; here a crew-day of 600 minutes is "cut" into vegetation tasks.
The master LP is solved with GLOP through `mathopt.IncrementalSolver`, as in the sample; the
pricing knapsack is solved with HiGHS instead of CP-SAT.
"""

from __future__ import annotations

import math

from ortools.math_opt.python import mathopt

DAY = 600                                   # minutes of work in one crew-day
#: task -> (minutes per task, tasks to do this season). Invented for the lesson; GridCap is fictional.
TASKS = {
    "trim span": (55, 48),
    "hazard tree": (110, 30),
    "clear corridor": (250, 22),
    "widen right-of-way": (340, 14),
    "storm debris": (190, 17),
}


def price_pattern(prices: dict[str, float], tasks=TASKS, day: int = DAY) -> tuple[float, dict[str, int]]:
    """The pricing problem: the crew-day whose tasks are worth the most at the master's prices."""
    m = mathopt.Model(name="pricing")
    a = {t: m.add_integer_variable(lb=0, ub=need, name=f"a_{t}") for t, (_, need) in tasks.items()}
    m.add_linear_constraint(sum(minutes * a[t] for t, (minutes, _) in tasks.items()) <= day, name="day")
    m.maximize(sum(prices[t] * a[t] for t in tasks))
    result = mathopt.solve(m, mathopt.SolverType.HIGHS, params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    if result.termination.reason != mathopt.TerminationReason.OPTIMAL:
        raise RuntimeError(result.termination.reason.name)
    return result.objective_value(), {t: round(result.variable_values(a[t])) for t in tasks if result.variable_values(a[t]) > 0.5}


def column_generation(tasks=TASKS, day: int = DAY, verbose: bool = True):
    master = mathopt.Model(name="crew days")
    cover = {t: master.add_linear_constraint(lb=need, name=f"cover_{t}") for t, (_, need) in tasks.items()}
    patterns: list[tuple[mathopt.Variable, dict[str, int]]] = []

    def add_pattern(pattern: dict[str, int]) -> None:
        lam = master.add_variable(lb=0, name=f"days_{len(patterns)}")
        master.objective.set_linear_coefficient(lam, 1)
        for t, count in pattern.items():
            cover[t].set_coefficient(lam, count)
        patterns.append((lam, pattern))

    for t, (minutes, need) in tasks.items():          # start: one single-task day per task
        add_pattern({t: min(need, day // minutes)})
    solver = mathopt.IncrementalSolver(master, mathopt.SolverType.GLOP)
    history, best = [], 0.0
    while True:
        lp = solver.solve()
        if lp.termination.reason != mathopt.TerminationReason.OPTIMAL or not lp.has_dual_feasible_solution():
            raise RuntimeError("master LP not solved")
        prices = {t: lp.dual_values(cover[t]) for t in tasks}
        worth, pattern = price_pattern(prices, tasks, day)
        lower = lp.objective_value() / max(worth, 1.0)          # no plan uses fewer days than this
        best = max(best, lower)
        history.append((len(history) + 1, lp.objective_value(), best, worth, pattern))
        if verbose:
            show = ", ".join(f"{n} {t}" for t, n in pattern.items())
            print(f"iter {len(history):2}  master LP {lp.objective_value():7.3f}  best bound {best:7.3f}"
                  f"  best day worth {worth:5.3f}  reduced cost {1 - worth:+.3f}  [{show}]")
        if worth <= 1 + 1e-6:                                    # no day has negative reduced cost
            break
        add_pattern(pattern)
    for lam, _ in patterns:
        lam.integer = True
    final = mathopt.solve(master, mathopt.SolverType.HIGHS, params=mathopt.SolveParameters(relative_gap_tolerance=0.0))
    used = [(round(final.variable_values(lam)), pattern) for lam, pattern in patterns if final.variable_values(lam) > 0.5]
    return lp.objective_value(), round(final.objective_value()), used, history, len(patterns)


if __name__ == "__main__":
    z_lp, z_ip, used, history, columns = column_generation()
    print(f"LP optimum {z_lp:.3f} after {len(history)} master solves, {columns} columns; "
          f"no plan uses fewer than {math.ceil(z_lp - 1e-6)} crew-days")
    print(f"integer master over those columns: {z_ip} crew-days")
    for n, pattern in used:
        minutes = sum(TASKS[t][0] * c for t, c in pattern.items())
        print(f"  {n:2} x  " + ", ".join(f"{c} {t}" for t, c in pattern.items()) + f"  ({minutes} min)")
