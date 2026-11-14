"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from depot import plan_depot

buses = {
    "route7": [("wash", 1), ("service", 2), ("inspect", 1)],
    "route9": [("service", 3), ("wash", 1)],
    "route12": [("inspect", 2), ("wash", 2)],
}

start = plan_depot(buses)
for (bus, k), hour in sorted(start.items()):
    print(f"{bus} step {k} ({buses[bus][k][0]}) starts at hour:", hour)
print("last bus leaves at hour:", max(start[b, len(s) - 1] + s[-1][1] for b, s in buses.items()))
