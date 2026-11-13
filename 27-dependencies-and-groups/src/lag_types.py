"""Lesson 6.5.4: start-to-start and finish-to-start lags, both written as start-to-start rows.

GridCap is a fictional utility's portfolio. Its data gives each child a start-to-start lag; the
finish-to-start reading below is the lesson's.
"""

from gridcap import generate
from planning_model import add_after, build, money, schedule, solve_highs

small = generate("small")
children = [c for c in small.projects if c.parent]


def start_to_start(parent, child) -> int:
    return child.parent_lag                         # child starts >= parent starts + lag


def finish_to_start(parent, child) -> int:
    return parent.duration + child.parent_lag       # child starts >= parent finishes + lag


for c in children:
    p = small.project(c.parent)
    print(f"{c.project_id} after {p.project_id}: lag {c.parent_lag}, {p.project_id} works {p.duration} year(s) "
          f"and may start {list(p.starts())}; {c.project_id} may start {list(c.starts())}")
    for name, rule in [("start-to-start", start_to_start), ("finish-to-start", finish_to_start)]:
        lag = rule(p, c)
        usable = [t for t in c.starts() if any(s <= t - lag for s in p.starts())]
        print(f"  {name:15} start-to-start lag {lag}: {c.project_id} can use {usable}")

for name, rule in [("start-to-start", start_to_start), ("finish-to-start", finish_to_start)]:
    plan = build(small, parents=False)
    for c in children:
        p = small.project(c.parent)
        add_after(plan, p, c, rule(p, c))
    result = solve_highs(plan.model)
    starts = schedule(plan, result)
    shown = {i: starts.get(i, "-") for c in children for i in (c.parent, c.project_id)}
    print(f"{name:15} NPV {money(result.objective_value())}  {shown}")
