"""The message callback: a solver's log, line by line, into your program instead of the terminal.

`printer_message_callback(prefix=...)` comes from the OR-Tools example `remote_solve.py`,
https://github.com/google/or-tools/blob/stable/ortools/math_opt/samples/python/remote_solve.py
"""

from ortools.math_opt.python import mathopt

from gridcap import generate
from plan_model import build, solve

small = generate("small")
pm = build(small)

log: list[str] = []
result = solve(pm.model, mathopt.SolverType.HIGHS, msg_cb=mathopt.list_message_callback(log))
print(f"{result.termination.reason.name}: {len(log)} log lines kept, none printed")
for line in log:
    if line.strip().startswith(("Status", "Primal bound", "Dual bound", "Gap")):
        print("  ", line.strip())

tiny = generate("tiny")
pm = build(tiny)
printer = mathopt.printer_message_callback(prefix="SCIP> ")     # prints each line as it arrives
keep = ("SCIP Status", "Primal Bound", "Dual Bound", "Gap")
# mathopt.solve, not plan_model.solve: that one silences standard output, the printer's too.
result = mathopt.solve(pm.model, mathopt.SolverType.GSCIP,
                       msg_cb=lambda lines: printer([line for line in lines if line.startswith(keep)]))
