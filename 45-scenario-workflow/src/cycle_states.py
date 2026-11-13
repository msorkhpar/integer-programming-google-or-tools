"""Lesson 12.1.3: the transition table, one scenario walked from Initial to Budget Lock, and the refusals.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.
"""

from gridcap import generate
from cycle import ACTIONS, STATES, TRANSITIONS, Refused, Service
from scenario import Clock, create, optimize

print(f"{'state':<12}" + "".join(f"{a:<13}" for a in ACTIONS))
for state in STATES:
    print(f"{state:<12}" + "".join(f"{TRANSITIONS.get((state, a), 'refused'):<13}" for a in ACTIONS))

small = generate("small")
clock = Clock()
svc = Service()
v = svc.add(create(small, "small", "S-001", "base", by="planner-a", at=clock.now()), cycle="2027 plan")


def attempt(label, fn):
    try:
        out = fn()
        _, state, version = svc.read("S-001")
        print(f"{label:<28} ok       -> {state}, version {version}")
        return out
    except Refused as e:
        print(f"{label:<28} refused: {e}")


attempt("optimize in Initial", lambda: svc.start_run("S-001"))
v = attempt("check", lambda: svc.check("S-001", v))
attempt("lock in Pre-Opt", lambda: svc.lock("S-001", v, "manager-a"))
ticket = svc.start_run("S-001")
v = attempt("optimize", lambda: svc.finish_run(ticket, optimize(ticket.inputs)))
v = attempt("lock", lambda: svc.lock("S-001", v, "manager-a"))
s, _, _ = svc.read("S-001")
s.budget[2031] = 7000
attempt("edit the locked scenario", lambda: svc.edit("S-001", v, s))
attempt("optimize the locked one", lambda: svc.start_run("S-001"))
svc.copy("S-001", "S-002", "after-lock change", by="planner-b", at=clock.now())
_, state, version = svc.read("S-002")
print(f"copy of the locked scenario: S-002 is {state}, version {version}, parent {svc.read('S-002')[0].parent_id}")
