"""A "why" line for every project of GridCap small: what reversing its decision costs, and the rules that make it so (lesson 9.3.2)."""

from collections import defaultdict

from gridcap import generate

from explain_model import Scenario, build, solve
from why import changes, force, rules_against

small = generate("small")
scenario = Scenario()
base = solve(build(small, scenario))

print("WHY DEFERRED: projects out of the plan, cheapest to force in first")
deferred = [force(small, scenario, base, p.project_id) for p in small.projects if p.project_id not in base.plan]
for f in sorted(deferred, key=lambda f: (f.cost, f.pid)):
    added, dropped, moved = changes(base.plan, f.plan)
    print(f"  {f.pid}  costs {f.cost:5,}  gives way: {', '.join(dropped)}")
    for rule in rules_against(small, base, f.pid):
        print(f"        {rule}")
print()

print("WHY SELECTED: projects in the plan, by what losing them costs")
selected = [force(small, scenario, base, pid) for pid in sorted(base.plan)]
for f in sorted(selected, key=lambda f: (f.cost is not None, -(f.cost or 0), f.pid)):
    p = small.project(f.pid)
    if f.cost is None:
        print(f"  {f.pid}  {f.status}: must_{f.pid} keeps a must-do in every plan")
    else:
        print(f"  {f.pid}  losing it costs {f.cost:5,}  (its NPV {p.npv[base.plan[f.pid]]:5,})")
print()

print("WHY LATE: projects that start after their earliest year, pinned to it")
for pid, t in sorted(base.plan.items()):
    first = small.project(pid).earliest_start
    if t > first:
        f = force(small, scenario, base, pid, first)
        added, dropped, moved = changes(base.plan, f.plan)
        print(f"  {pid}  {t} -> {first} costs {f.cost:4,}  dropped {dropped}  moved {len(moved)}")
print()

same = defaultdict(list)
for f in deferred + selected:
    if f.cost is not None:
        same[tuple(sorted(f.plan.items()))].append(f"{f.pid} {f.action}")
print("forcings that land on the same plan:")
for plan, names in sorted(same.items(), key=lambda kv: -len(kv[1])):
    if len(names) > 1:
        cost = round(base.npv - sum(small.project(p).npv[t] for p, t in plan))
        print(f"  cost {cost:4,}: {', '.join(names)}")
