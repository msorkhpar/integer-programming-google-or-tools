"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from windows import build

# A boiler engineer's three flats, in minutes.
travel = [
    [0, 15, 25, 10],
    [15, 0, 8, 20],
    [25, 8, 0, 12],
    [10, 20, 12, 0],
]
service = [0, 40, 25, 30]


def allowed(windows, plan, shift_end=240, max_wait=30):
    manager, routing = build(travel, service, windows, shift_end, max_wait)
    return routing.ReadAssignmentFromRoutes([plan], True) is not None


windows = {1: (0, 30), 2: (50, 100), 3: (90, 160)}
print("windows 1:0-30 2:50-100 3:90-160, order [1, 2, 3]:", allowed(windows, [1, 2, 3]))
print("same windows, order [3, 2, 1]:", allowed(windows, [3, 2, 1]))
print("flat 3 opens at 200, max wait 30:", allowed({**windows, 3: (200, 230)}, [1, 2, 3]))
print("flat 3 opens at 200, max wait 90:", allowed({**windows, 3: (200, 230)}, [1, 2, 3], max_wait=90))
print("shift ends at 120:", allowed(windows, [1, 2, 3], shift_end=120))
