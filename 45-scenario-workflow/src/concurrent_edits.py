"""Lesson 12.1.3: a stale write refused, a run that finished on old inputs refused, one lock per cycle.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.
The people (`planner-a`, ...) are placeholders.
"""

from gridcap import generate
from cycle import Refused, Service
from scenario import Clock, copy_scenario, create, optimize

small = generate("small")
clock = Clock()
svc = Service()
svc.add(create(small, "small", "S-001", "base", by="planner-a", at=clock.now()), cycle="2027 plan")

# Two planners read the same version, change different budgets, and save.
a, _, va = svc.read("S-001")
b, _, vb = svc.read("S-001")
print(f"planner-a and planner-b both read version {va}")
a.budget[2029] = 8000
print("planner-a saves 2029 = 8000:   version", svc.edit("S-001", va, a))
b.budget[2031] = 7000
try:
    svc.edit("S-001", vb, b)
except Refused as e:
    print("planner-b saves 2031 = 7000:  refused:", e)
b, _, vb = svc.read("S-001")
b.budget[2031] = 7000
print("planner-b reads again, saves:  version", svc.edit("S-001", vb, b),
      "| budgets 2029 and 2031:", svc.read("S-001")[0].budget[2029], svc.read("S-001")[0].budget[2031])

# A run starts, a planner edits while it runs, the run finishes on the old inputs.
v = svc.check("S-001", svc.read("S-001")[2])
ticket = svc.start_run("S-001")
s, _, v = svc.read("S-001")
s.budget[2030] = 8000
print(f"run started at version {ticket.version}; planner-a edits 2030 meanwhile: version {svc.edit('S-001', v, s)}")
stale = optimize(ticket.inputs)
try:
    svc.finish_run(ticket, stale)
except Refused as e:
    print("run finished, attach:", "refused:", e)
ticket = svc.start_run("S-001")
v = svc.finish_run(ticket, optimize(ticket.inputs))
rec = svc.records["S-001"]
print(f"rerun on version {ticket.version}: attached, {rec.state}, NPV ${rec.result.npv:,}k (the stale run said ${stale.npv:,}k)")

# One plan of record per cycle.
svc.lock("S-001", v, by="manager-a")
other = copy_scenario(rec.scenario, "S-002", "alternative", by="planner-b", at=clock.now())
svc.add(other, cycle="2027 plan")
v2 = svc.check("S-002", 1)
t2 = svc.start_run("S-002")
v2 = svc.finish_run(t2, optimize(t2.inputs))
try:
    svc.lock("S-002", v2, by="manager-b")
except Refused as e:
    print("lock S-002:", "refused:", e)
