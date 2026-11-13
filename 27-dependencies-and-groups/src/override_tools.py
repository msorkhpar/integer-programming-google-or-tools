"""Manual overrides for the module 27 planning model, applied as bounds and undone by restoring them.

Fixing a start variable through its bounds is how the OR-Tools MathOpt sample
`time_indexed_scheduling.py` enforces release times (`v.upper_bound = 0` for a start before the
release). GridCap is a fictional utility's portfolio.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Override:
    pid: str
    kind: str              # "in" (fund, any year), "year" (start in `year`), "out" (never), "not_before"
    year: int | None = None


def apply(plan, o: Override) -> list:
    """Apply one override; return what undoes it: (variable, old lower, old upper) or a row to delete."""
    undo = []
    years = plan.portfolio.project(o.pid).starts()
    if o.kind == "in":                                   # a rule on a sum of variables: a row
        row = plan.model.add_linear_constraint(plan.started(o.pid) == 1, name=f"override_{o.pid}")
        return [row]
    for t in years:
        v = plan.x[o.pid, t]
        undo.append((v, v.lower_bound, v.upper_bound))
        if o.kind == "out" or (o.kind == "not_before" and t < o.year) or (o.kind == "year" and t != o.year):
            v.upper_bound = 0
        if o.kind == "year" and t == o.year:
            v.lower_bound = 1
    return undo


def undo(plan, changes: list) -> None:
    for change in changes:
        if isinstance(change, tuple):
            v, lower, upper = change
            v.lower_bound, v.upper_bound = lower, upper
        else:
            plan.model.delete_linear_constraint(change)
