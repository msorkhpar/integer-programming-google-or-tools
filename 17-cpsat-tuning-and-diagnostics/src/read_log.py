"""Lesson 4.6.4: the CP-SAT log of the GridCap small plan, section by section.

GridCap is a fictional utility's portfolio. One worker, so the log's content repeats run to run,
except for the times it measures; `mask` replaces every measured time with <time>.
"""

import re

from ortools.sat.python import cp_model

from cpsat_plan import build
from gridcap import generate

TIME = re.compile(r"\b\d+(\.\d+)?(e[-+]?\d+)?(s|ms|us|ns)\b")
CLOCK = re.compile(r"\b(walltime|usertime|time): [\d.e+-]+")


def mask(line: str) -> str:
    """The log line with every wall-clock measurement replaced by <time>."""
    return CLOCK.sub(r"\1: <time>", TIME.sub("<time>", line))


def section(log: list[str], first: str, last: str | None = None) -> list[str]:
    """The lines from the one starting with `first` to the next starting with `last` (or a blank)."""
    start = next(i for i, line in enumerate(log) if line.startswith(first))
    out = []
    for line in log[start:]:
        if out and (line.startswith(last) if last else not line.strip()):
            break
        out.append(line)
    return out


plan = build(generate("small"))
solver = cp_model.CpSolver()
solver.parameters.num_workers = 1
solver.parameters.log_search_progress = True     # write the log ...
solver.parameters.log_to_stdout = False          # ... but not to the screen:
log: list[str] = []
solver.log_callback = log.append                 # every line comes here instead
status = solver.solve(plan.model)
log = [mask(line) for text in log for line in (text.splitlines() or [""])]

for title, lines in (
    ("header", section(log, "Starting CP-SAT solver", "Initial optimization model")),
    ("model as written", section(log, "Initial optimization model")),
    ("presolve summary, the lines about variables", [line for line in section(log, "Presolve summary")
                                                     if "affine relations" in line or "unused variables" in line]),
    ("model after presolve", section(log, "Presolved optimization model")),
    ("search", section(log, "Preloading model.", "Task timing")),
    ("response", section(log, "CpSolverResponse summary")),
):
    print(f"==== {title}")
    print("\n".join(line for line in lines if line.strip()))
print("==== the same numbers from the solver object")
print(f"status {solver.status_name(status)}, objective {solver.objective_value:,.0f}, "
      f"bound {solver.best_objective_bound:,.0f}, branches {solver.num_branches:,}, "
      f"conflicts {solver.num_conflicts:,}")
print("solver.response_stats() starts with:", solver.response_stats().splitlines()[0])
