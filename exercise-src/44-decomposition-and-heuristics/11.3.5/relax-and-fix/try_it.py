"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from relax_fix import relax_and_fix

projects = {
    "tunnel": {"value": {2030: 11}, "cost": [8, 8]},
    "hydrants": {"value": {2030: 9}, "cost": [8]},
    "tower": {"value": {2031: 14, 2032: 10}, "cost": [8]},
    "kiosk": {"value": {2032: 4}, "cost": [3]},
}
budgets = {2030: 8, 2031: 8, 2032: 8}

print("window 1, keep 1:", relax_and_fix(projects, budgets, 1, 1))
print("window 2, keep 1:", relax_and_fix(projects, budgets, 2, 1))
print("window 3, keep 3:", relax_and_fix(projects, budgets, 3, 3))
