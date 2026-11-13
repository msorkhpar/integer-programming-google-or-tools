"""Budget-cut scenarios on one model and one solver: edit, re-solve, put back."""

import contextlib

from ortools.math_opt.python import mathopt

from gridcap import generate
from plan_model import EXACT, build, plan, quiet

small = generate("small")
pm = build(small)                                  # built once, for every scenario below


@contextlib.contextmanager
def edited(obj, attr: str, value: float):
    """Set obj.attr for the length of a `with` block, then put the old value back, even on errors."""
    old = getattr(obj, attr)
    setattr(obj, attr, value)
    try:
        yield
    finally:
        setattr(obj, attr, old)


with quiet(), mathopt.IncrementalSolver(pm.model, mathopt.SolverType.GSCIP) as solver:
    base = solver.solve(params=EXACT)
    base_plan = plan(pm, base.variable_values())
    rows = [f"base           NPV {base.objective_value():,.0f}"]
    for share in (0.05, 0.10, 0.20):
        row = pm.budget[2029]
        with edited(row, "upper_bound", (1 - share) * small.budget[2029]):
            result = solver.solve(params=EXACT)
            cut_plan = plan(pm, result.variable_values())
            dropped = sorted(set(base_plan) - set(cut_plan))
            moved = sorted(p for p in cut_plan if p in base_plan and cut_plan[p] != base_plan[p])
            rows.append(f"2029 cut {share:4.0%}  NPV {result.objective_value():,.0f}"
                        f"  dropped {dropped}  moved {moved}")
    rows.append(f"2029 bound after the loop: {pm.budget[2029].upper_bound:,.0f}")

    # A project ruled out for one scenario: bound its start variables to 0, never delete them.
    with contextlib.ExitStack() as stack:
        for t in small.project("P032").starts():
            stack.enter_context(edited(pm.x["P032", t], "upper_bound", 0.0))
        result = solver.solve(params=EXACT)
        rows.append(f"without P032   NPV {result.objective_value():,.0f}")
    again = solver.solve(params=EXACT)
    rows.append(f"all restored   NPV {again.objective_value():,.0f}")
print("\n".join(rows))

# The trap: relative edits that are never undone pile up.
for scenario in ("5% cut", "another 5% cut"):
    pm.budget[2029].upper_bound *= 0.95
    print(f"{scenario:15} 2029 bound {pm.budget[2029].upper_bound:,.2f}"
          f"  (budget {small.budget[2029]:,}, cut {1 - pm.budget[2029].upper_bound / small.budget[2029]:.2%})")

# Deleting a variable invalidates every reference to it.
spare = pm.x["P040", 2028]
pm.model.delete_variable(spare)
try:
    spare.upper_bound = 1.0
except Exception as error:
    print("using a deleted variable:", type(error).__name__, "|", error)
