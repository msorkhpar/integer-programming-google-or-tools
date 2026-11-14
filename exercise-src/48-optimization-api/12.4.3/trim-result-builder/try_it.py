"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import math

from trim_builder import build_result

work = {"L-1": (6, 70), "L-4": (7, 50), "L-6": (6, 30), "L-8": (8, 45)}
capacity = {8: 120, 6: 140, 7: 100}

done = build_result("optimal", "Best plan found and proven.", 180.0, 180.0, ["L-6", "L-1", "L-4"], work, capacity)
print("optimal, L-6 L-1 L-4:", done.circuits, "gap", done.gap)
print("hours by month:", [(m.month, m.crew_hours, m.capacity) for m in done.hours_by_month])
stopped = build_result("time_limit", "Stopped at the limit.", 120.0, 150.0, ["L-8"], work, capacity)
print("time_limit, value 120, bound 150: gap", stopped.gap)
empty = build_result("time_limit", "No plan found within the limit.", None, math.inf, [], work, capacity)
print("no plan, infinite bound:", empty.model_dump_json())
