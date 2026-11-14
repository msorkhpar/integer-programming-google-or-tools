"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from lns_step import lns_step

projects = {
    "sewer": {"value": {2030: 12, 2031: 16}, "cost": [8]},
    "hydrants": {"value": {2030: 9, 2031: 5}, "cost": [8]},
    "kiosk": {"value": {2030: 6}, "cost": [4]},
    "signs": {"value": {2031: 3}, "cost": [4]},
}
budgets = {2030: 12, 2031: 12}
start = {"sewer": 2030}

print("start plan:", start)
print("free hydrants, kiosk:", lns_step(projects, budgets, start, {"hydrants", "kiosk"}))
print("free sewer, hydrants:", lns_step(projects, budgets, start, {"sewer", "hydrants"}))
print("free everything:", lns_step(projects, budgets, {}, set(projects)))
