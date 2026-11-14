"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from flow import ship

def r(v):
    return v if v is None else round(v, 2)


# Two depots, one hub and two shelters; each arc is (cost per crate, capacity).
arcs = {("D1", "S1"): (4, 30), ("D1", "Hub"): (1, 40), ("D2", "Hub"): (2, 40),
        ("Hub", "S1"): (1, 25), ("Hub", "S2"): (2, 60)}

status, cost, flows = ship({"D1": 50, "D2": 30}, {"S1": 35, "S2": 30}, arcs)
print("supply 50/30, demand 35/30:", status, r(cost))
for arc, amount in (flows or {}).items():
    print(f"  flow on {arc[0]}->{arc[1]}:", r(amount))
print("supply 50/30, demand 50/40:", ship({"D1": 50, "D2": 30}, {"S1": 50, "S2": 40}, arcs))
