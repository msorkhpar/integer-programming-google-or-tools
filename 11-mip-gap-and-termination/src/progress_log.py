"""One HiGHS run of GridCap medium's selection MILP, watched through its log's progress table."""

from ortools.math_opt.python import mathopt

from gridcap import generate
from selection import build, mask_time, solve_highs

sel = build(generate("medium"))
log: list[str] = []
result = solve_highs(sel.model, mathopt.SolveParameters(node_limit=100, relative_gap_tolerance=0.0,
                                                        enable_output=True), log=log)

start = next(i for i, line in enumerate(log) if line.strip().startswith("Nodes"))
end = next(i for i, line in enumerate(log) if line.startswith("Solving report"))
for line in log[start:end]:
    if line.strip():
        print(mask_time(line))
for line in log[end:]:
    if line.strip().startswith(("Status", "Primal bound", "Dual bound", "Gap", "Nodes")):
        print(line.strip())
