"""Lesson 6.5.6: overrides that contradict the model's rules, found before the solve.

GridCap is a fictional utility's portfolio; the overrides are invented for the lesson.
"""

from gridcap import generate
from override_tools import Override, apply
from planning_model import build, groups_of, schedule, solve_highs, status

small = generate("small")


def funds(o: Override) -> bool:
    return o.kind in ("in", "year")


def check(overrides: list[Override]) -> list[str]:
    """Conflicts between the overrides and the rules, readable by a planner."""
    problems = []
    out = {o.pid for o in overrides if o.kind == "out"}
    funded = {o.pid for o in overrides if funds(o)}
    for o in overrides:
        p = small.project(o.pid)
        if o.year is not None and o.kind == "year" and o.year not in p.starts():
            problems.append(f"{o.pid} cannot start in {o.year}: its window is {p.earliest_start}-{p.latest_start}")
        if o.pid in out and p.must_do:
            problems.append(f"{o.pid} is a must-do and cannot be overridden out")
        if o.pid in funded and p.parent in out:
            problems.append(f"{o.pid} is forced in, but its parent {p.parent} is forced out")
    for g, members in groups_of(small).items():
        both = [i for i in members if i in funded]
        if len(both) > 1:
            problems.append(f"{both} are forced in, but they are alternatives ({g})")
    return problems


cases = {
    "child in, parent out": [Override("P023", "year", 2029), Override("P022", "out")],
    "both alternatives in": [Override("P030", "in"), Override("P031", "in")],
    "must-do out": [Override("P017", "out")],
    "outside the window": [Override("P038", "year", 2029)],
}
for label, overrides in cases.items():
    found = check(overrides)
    plan = build(small)
    for o in overrides:
        apply(plan, o)
    result = solve_highs(plan.model)
    solved = status(result)
    if solved == "OPTIMAL":
        starts = schedule(plan, result)
        solved += " with " + ", ".join(f"{o.pid} {starts.get(o.pid, 'not funded')}" for o in overrides)
    print(f"{label}: {found}; solve {solved}")
