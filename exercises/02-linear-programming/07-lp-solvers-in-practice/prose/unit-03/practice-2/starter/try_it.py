"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from what_if import build, what_if

model, budget = build()
for cut in (2, 4, 9):
    predicted, actual = what_if(model, budget, cut)
    print(f"cut {cut}: predicted", predicted, "actual", actual)
print("budget bound after the runs:", budget.upper_bound)
