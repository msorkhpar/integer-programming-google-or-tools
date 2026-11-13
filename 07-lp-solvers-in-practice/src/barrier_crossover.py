"""Lesson 2.4.1: what HiGHS's interior point method does on the funding LP, and what crossover changes."""

import highspy
from ortools.math_opt.python import mathopt

from funding_lp import build
from gridcap import generate
from solver_log import solve_with_log

lp = build(generate("medium"))


# The LP handed to HiGHS through its own API, interior point only, with presolve off so that every
# variable goes through the interior point method, and crossover "on" or "off".
def solve_ipm(crossover: str) -> tuple[highspy.Highs, dict]:
    h = highspy.Highs()
    for option, value in (("output_flag", False), ("solver", "ipm"), ("presolve", "off"),
                          ("run_crossover", crossover)):
        h.setOptionValue(option, value)
    inf = highspy.kHighsInf
    column = {var: h.addVariable(lb=max(var.lower_bound, -inf), ub=min(var.upper_bound, inf), name=var.name)
              for var in lp.model.variables()}
    for row in lp.model.linear_constraints():
        terms = list(row.terms())
        h.addRow(max(row.lower_bound, -inf), min(row.upper_bound, inf), len(terms),
                 [column[t.variable].index for t in terms], [t.coefficient for t in terms])
    h.maximize(sum(t.coefficient * column[t.variable] for t in lp.model.objective.linear_terms()))
    return h, column


def inside_counts(crossover: str) -> tuple[highspy.Highs, list[int]]:
    """How many variables sit strictly inside their bounds, by more than 0, 1e-12, 1e-9 and 1e-6."""
    h, column = solve_ipm(crossover)
    x = h.getSolution().col_value
    room = [min(x[c.index] - var.lower_bound, var.upper_bound - x[c.index]) for var, c in column.items()]
    counts = [sum(1 for r in room if r > tol) for tol in (0, 1e-12, 1e-9, 1e-6)]
    return h, counts


if __name__ == "__main__":
    # 1. The barrier's progress table, one row per iteration, from the HiGHS log.
    barrier = mathopt.SolveParameters(lp_algorithm=mathopt.LPAlgorithm.BARRIER)
    result, log = solve_with_log(lp.model, mathopt.SolverType.HIGHS, barrier)
    start = log.index("Interior point solve") + 1
    end = next(i for i, line in enumerate(log) if line.startswith("Running crossover"))
    print("HiGHS log, interior point iterations:")
    for line in log[start:end]:
        print(line)

    # 2. Crossover off, then on.
    print(f"{'crossover':9} {'status':8} {'objective':>16}   variables strictly inside their bounds, by more than")
    print(f"{'':9} {'':8} {'':>16}   {'0':>5} {'1e-12':>6} {'1e-9':>5} {'1e-6':>5}")
    for crossover in ("off", "on"):
        h, counts = inside_counts(crossover)
        print(f"{crossover:9} {h.getModelStatus().name[1:]:8} {h.getInfo().objective_function_value:16.6f}   "
              f"{counts[0]:5} {counts[1]:6} {counts[2]:5} {counts[3]:5}   of {h.getNumCol()}")
