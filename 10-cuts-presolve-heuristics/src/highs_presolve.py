"""HiGHS's presolve on the five-year selection model: the log lines, with presolve on and off."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import five_year, solve_with_log

model = five_year(generate("medium")).model
for label, presolve in (("presolve on (default)", None), ("presolve off", mathopt.Emphasis.OFF)):
    result, log = solve_with_log(model, mathopt.SolveParameters(presolve=presolve))
    print(f"--- {label}")
    start = next(i for i, line in enumerate(log) if line.startswith(("Presolving", "Solving MIP")))
    for line in log[start:]:
        if line.startswith("Src:"):
            break
        if line.strip():
            print(line)
    print(f"status {result.termination.reason.name}, value {result.objective_value():,.0f}, "
          f"nodes {result.solve_stats.node_count}")
