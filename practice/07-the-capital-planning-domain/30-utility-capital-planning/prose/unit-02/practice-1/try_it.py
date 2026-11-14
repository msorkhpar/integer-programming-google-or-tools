"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from trims import plan_trims

circuits = {"North": (40, 2026), "East": (25, 2027), "South": (35, 2027), "West": (15, 2028)}

plan = plan_trims(circuits, 4, 50, [2030, 2031, 2032, 2033])
for year, (trimmed, backlog) in plan.items():
    print(f"{year} at 50 miles a year: trimmed {trimmed}, miles left due {backlog}")
