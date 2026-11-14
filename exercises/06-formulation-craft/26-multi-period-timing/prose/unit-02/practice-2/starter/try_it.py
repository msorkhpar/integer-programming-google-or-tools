"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from steady import Project, allowed

# Lining projects: id, spend per year of work, allowed start years.
years = [2031, 2032, 2033]
works = [
    Project("L1", (70, 70), (2031, 2032)),
    Project("L2", (150,), (2031, 2032, 2033)),
    Project("L3", (40,), (2031, 2032, 2033)),
]

print("L1 2031, L3 2033 at step 80:", allowed(works, years, 80, {"L1": 2031, "L3": 2033}))
print("L2 2032 at step 80:", allowed(works, years, 80, {"L2": 2032}))
print("L2 2032 at step 150:", allowed(works, years, 150, {"L2": 2032}))
print("L1 2032, L3 2031 at step 30:", allowed(works, years, 30, {"L1": 2032, "L3": 2031}))
