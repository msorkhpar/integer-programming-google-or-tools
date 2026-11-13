"""Where the time of one planning run goes: data, build, hand-off and solve, each on its own clock.

The run is GridCap's timing model (lessons 6.4.1-6.4.2) on the medium and large portfolios, solved
by HiGHS to a 1% gap. Wall times change from run to run and machine to machine: the program
prints them in a block of their own, after the lines that repeat. GridCap is fictional.
"""

from __future__ import annotations

import time

from ortools.math_opt.python import mathopt

from gridcap import generate
from loop_builder import build_loops, solve_highs
from stopwatch import measure

PARAMS = mathopt.SolveParameters(relative_gap_tolerance=0.01)


def one_run(size: str) -> tuple[dict[str, float], mathopt.Model, mathopt.SolveResult]:
    """One planning run, the way a service does it, with a clock around each phase."""
    clock = {}
    start = time.perf_counter()
    portfolio = generate(size)
    clock["data"] = time.perf_counter() - start

    start = time.perf_counter()
    model = build_loops(portfolio)
    clock["build"] = time.perf_counter() - start

    start = time.perf_counter()
    result = solve_highs(model, PARAMS)
    wall = time.perf_counter() - start
    clock["solve"] = result.solve_stats.solve_time.total_seconds()    # what the solver reports
    clock["hand-off"] = wall - clock["solve"]                          # the rest of mathopt.solve
    return clock, model, result


if __name__ == "__main__":
    measured = {}
    for size in ("medium", "large"):
        runs = [one_run(size) for _ in range(3)]
        _, model, result = runs[-1]
        nonzeros = sum(1 for _ in model.linear_constraint_matrix_entries())
        print(f"{size:6}: {model.get_num_variables():,} variables, {model.get_num_linear_constraints():,} rows, "
              f"{nonzeros:,} nonzeros; {result.termination.reason.name}, NPV {result.objective_value():,.0f}k")
        measured[size] = runs
    print()
    print("measured (3 runs each; medians, then each phase's share of the median total):")
    for size, runs in measured.items():
        medians = {k: sorted(r[0][k] for r in runs)[1] for k in ("data", "build", "hand-off", "solve")}
        total = sum(medians.values())
        cells = "  ".join(f"{k} {v:.3f}s ({v / total:.0%})" for k, v in medians.items())
        print(f"{size:6}: {cells}")

    large = generate("large")
    lp = build_loops(large)
    for v in lp.variables():
        v.integer = False
    build = measure(lambda: build_loops(large), repeats=3)
    solve = measure(lambda: solve_highs(lp), repeats=3)
    print(f"large LP relaxation: build {build}; HiGHS solve {solve}")
