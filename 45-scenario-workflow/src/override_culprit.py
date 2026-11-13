"""Lesson 12.1.2: a set of overrides makes the scenario infeasible; the trail finds which ones.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.
The people (`planner-a`, ...) and their reasons are invented placeholders.
"""

from gridcap import generate
from overrides import Override, request
from scenario import Clock, copy_scenario, create, optimize

small = generate("small")
clock = Clock()
base = create(small, "small", "S-001", "base", by="planner-a", at=clock.now())
s = copy_scenario(base, "S-003", "early-starts", by="planner-a", at=clock.now())
trail = []
for o, by, why in [
    (Override("P021", "not_before", 2030), "planner-c", "outage window"),
    (Override("P032", "start_in", 2027), "planner-b", "line rating expires in 2027"),
    (Override("P034", "start_in", 2027), "planner-a", "substation tie-in agreed for 2027"),
    (Override("P038", "start_in", 2027), "planner-a", "same outage as P034"),
]:
    e = request(s, trail, o, small, by=by, at=clock.now(), why=why)
    print(f"#{e.seq} {e.action:<7} {o.text():<19} problems: {list(e.changes) if e.action == 'refused' else 'none'}")

print("solve with all four:", optimize(s).status)
print("2027 budget", small.budget[2027], "| forced into 2027:",
      " + ".join(str(small.project(p).spend(2027)[2027]) for p in ("P032", "P034", "P038")))


def culprits(s, trail) -> list:
    """Drop one override at a time, newest first; keep it dropped if the scenario stays infeasible."""
    keep = {e.override.project: e for e in trail if e.action == "set"}
    for e in sorted(keep.values(), key=lambda e: -e.seq):
        trial = {p: x.override for p, x in keep.items() if p != e.override.project}
        s.overrides = trial
        if optimize(s).status == "INFEASIBLE":
            del keep[e.override.project]
    s.overrides = {p: x.override for p, x in keep.items()}
    return sorted(keep.values(), key=lambda e: e.seq)


for e in culprits(s, trail):
    print(f"needed for the conflict: #{e.seq} {e.override.text():<19} by {e.by} at {e.at}: {e.why}")
print("solve with only those:", optimize(s).status)
