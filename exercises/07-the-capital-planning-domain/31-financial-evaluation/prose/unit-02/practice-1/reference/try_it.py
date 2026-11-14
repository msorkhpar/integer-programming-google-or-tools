"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from contract import billed

estimate = (600, 300, 150)

print("priced 2025, start 2025, 3%:", {y: round(v, 2) for y, v in billed(estimate, 2025, 2025, 0.03).items()})
print("priced 2025, start 2028, 3%:", {y: round(v, 2) for y, v in billed(estimate, 2025, 2028, 0.03).items()})
print("priced 2025, start 2028, 0%:", {y: round(v, 2) for y, v in billed(estimate, 2025, 2028, 0.0).items()})
