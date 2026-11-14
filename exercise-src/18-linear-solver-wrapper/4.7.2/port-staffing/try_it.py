"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from staffing import legacy_plan, mathopt_plan

# kind -> (hours a crew covers, cost of a crew, most crews, union minimum)
yard = {"crews": {"dock": (35, 25, 5, 1), "crane": (45, 40, 3, 0), "temp": (20, 18, 6, 0)},
        "need_low": 150, "need_high": 190, "overtime_max": 30, "overtime_rate": 0.8}
print("legacy:", legacy_plan(yard))
print("mathopt:", mathopt_plan(yard))
tight = dict(yard, crews=dict(yard["crews"], dock=(35, 25, 5, 4), crane=(45, 40, 3, 2)))
print("legacy, minimums dock 4, crane 2:", legacy_plan(tight))
print("mathopt, minimums dock 4, crane 2:", mathopt_plan(tight))
