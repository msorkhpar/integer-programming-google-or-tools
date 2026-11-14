"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from reasons import why_deferred

groups = {"line_P1": "pipe_1", "swap_P1": "pipe_1", "line_P5": "pipe_5", "swap_P5": "pipe_5"}
best = {"swap_P1", "swap_P5", "tank_T3", "gate_G8"}

print("line_P1 forced in:", why_deferred("line_P1", groups, best, {"line_P1", "swap_P5", "gate_G8"}))
print("pump_Q2 forced in:", why_deferred("pump_Q2", groups, best, {"pump_Q2", "swap_P1", "tank_T3"}))
print("meter_M6 forced in:", why_deferred("meter_M6", groups, best, best | {"meter_M6"}))
print("line_P5 with no plan:", why_deferred("line_P5", groups, best, None))
