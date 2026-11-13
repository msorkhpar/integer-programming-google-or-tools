"""Lesson 12.1.2: overrides requested, refused, superseded and revoked, each one an audit entry.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.
The people (`planner-a`, ...) and their reasons are invented placeholders.
"""

from gridcap import generate
from overrides import Override, replay, request, revoke
from scenario import Clock, copy_scenario, create, diff_plans, optimize

small = generate("small")
clock = Clock()
base = create(small, "small", "S-001", "base", by="planner-a", at=clock.now())
s = copy_scenario(base, "S-002", "q2-overrides", by="planner-a", at=clock.now())
trail = []

asks = [
    (Override("P024", "start_in", 2029), "planner-a", "Ridge customers were promised a 2029 start"),
    (Override("P032", "out"), "planner-b", "waiting for the Valley line study"),
    (Override("P036", "not_before", 2029), "planner-c", "no Coast crew before 2029"),
    (Override("P038", "start_in", 2029), "planner-a", "bundle with P024 crews"),
    (Override("P017", "out"), "planner-b", "permit risk"),
    (Override("P021", "not_before", 2030), "planner-c", "outage window"),
    (Override("P024", "start_in", 2030), "planner-a", "promise moved to 2030 after the March review"),
]
for o, by, why in asks:
    request(s, trail, o, small, by=by, at=clock.now(), why=why)
revoke(s, trail, "P021", small, by="manager-a", at=clock.now(), why="outage window confirmed open in 2029")

for e in trail:
    print(e.line())
    for change in e.changes:
        print(f"      {change}")

print("in force:", [o.text() for o in s.overrides.values()])
print("replayed from the trail alone:", [o.text() for o in replay(trail, "S-002").values()])
print("replay equals the scenario:", replay(trail, "S-002") == s.overrides)

r_base, r_s = optimize(base), optimize(s)
print(f"base NPV ${r_base.npv:,}k  q2-overrides NPV ${r_s.npv:,}k  the overrides cost ${r_base.npv - r_s.npv:,}k")
print("base -> q2-overrides:", diff_plans(r_base, r_s))
