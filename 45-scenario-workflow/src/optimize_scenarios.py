"""Lesson 12.1.1: optimize is a function from a scenario to a result stamped with the scenario's snapshot.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.
"""

from gridcap import generate
from scenario import Clock, copy_scenario, create, diff_plans, optimize

small = generate("small")
clock = Clock()
base = create(small, "small", "S-001", "base", by="planner-a", at=clock.now())
cut = copy_scenario(base, "S-002", "cut-2030", by="planner-b", at=clock.now())
cut.budget[2030] = 7750


def show(r) -> str:
    return f"{r.scenario_id} {r.status} NPV ${r.npv:,}k funded {len(r.starts)} snapshot {r.snapshot[:12]}"


runs = {s.scenario_id: optimize(s) for s in (base, cut)}
for r in runs.values():
    print(show(r))
print("base -> cut-2030:", diff_plans(runs["S-001"], runs["S-002"]))

again = optimize(base)
print("base again: same plan", again.starts == runs["S-001"].starts, "| same NPV", again.npv == runs["S-001"].npv)


def current(r, s) -> bool:
    """A result describes the scenario only while the scenario still has the inputs it was solved with."""
    return r.snapshot == s.snapshot()


cut.budget[2031] = 7000
print("cut-2030 edited after its run; result current:", current(runs["S-002"], cut))
