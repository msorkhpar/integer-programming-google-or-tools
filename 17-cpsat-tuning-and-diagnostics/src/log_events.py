"""Lesson 4.6.4: the progress lines of a stopped GridCap medium run, read as a list of events.

GridCap is a fictional utility's portfolio. One worker and a deterministic limit, so the events repeat.
"""

import re

from ortools.sat.python import cp_model

from cpsat_plan import build
from gridcap import generate

EVENT = re.compile(r"^#(\d+|Bound|Done|Model)\s+(\S+)\s*(.*)$")
RANGE = re.compile(r"best:(\S+)\s+next:\[(\S+),(\S+)\]\s*(\S*)")


def events(log: list[str]) -> list[dict]:
    """One dict per progress line: kind ('solution', 'bound', 'done', 'model'), best, next range, worker."""
    out = []
    for line in log:
        m = EVENT.match(line)
        if not m:
            continue
        tag, rest = m.group(1), m.group(3)
        kind = "solution" if tag.isdigit() else tag.lower()
        found = RANGE.match(rest)
        if found:
            best, low, high, worker = found.groups()
            out.append({"kind": kind, "best": best, "next": (low, high), "worker": worker})
        else:
            out.append({"kind": kind, "best": None, "next": None, "worker": rest.split()[0] if rest else ""})
    return out


plan = build(generate("medium"))
solver = cp_model.CpSolver()
solver.parameters.num_workers = 1
solver.parameters.max_deterministic_time = 3.0
solver.parameters.log_search_progress = True
solver.parameters.log_to_stdout = False
log: list[str] = []
solver.log_callback = log.append
solver.solve(plan.model)

found = events(log)
solutions = [e for e in found if e["kind"] == "solution"]
bounds = [e for e in found if e["kind"] == "bound"]
print(f"{len(solutions)} solution lines, {len(bounds)} bound lines, last event: {found[-1]['kind']}")
print(f"plans: first {solutions[0]['best']}, last {solutions[-1]['best']}")
print(f"bound: from the domains {bounds[0]['next'][1]}, at the first plan {solutions[0]['next'][1]}, "
      f"at the end {found[-1]['next'][1]}")
print(f"response: objective {solver.objective_value:,.0f}, best_bound {solver.best_objective_bound:,.0f}")
