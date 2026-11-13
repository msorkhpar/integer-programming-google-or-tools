"""Which rows of GridCap small's best plan have no slack left (lesson 9.3.1)."""

from collections import defaultdict

from gridcap import generate

from binding import slack_table
from explain_model import TOL, build, solve

small = generate("small")
built = build(small)
run = solve(built)
print(f"{run.status}: NPV ${run.npv:,.0f}k, {len(run.plan)} of {len(small.projects)} projects funded")
print()

table = slack_table(built, run.plan)
rows, tight, least = defaultdict(int), defaultdict(int), {}
for name, fam, room in table:
    rows[fam] += 1
    tight[fam] += abs(room) <= TOL
    least[fam] = min(least.get(fam, room), room)
print("family  rows  binding  least slack")
for fam in rows:
    print(f"{fam:7} {rows[fam]:4}  {tight[fam]:7}  {least[fam]:11,.0f}")
print()

print("row          limit    used  slack")
for name, fam, room in table:
    if fam == "budget":
        limit = built.rows[name].upper_bound
        print(f"{name}  {limit:6,.0f}  {limit - room:6,.0f}  {room:5,.0f}")
