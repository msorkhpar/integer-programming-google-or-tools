"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from bound import Project, fractional_bound

# Four kitchen refits; the one in Leeds is ordered by the inspector.
refits = [
    Project("Leeds", 25, 40, must_do=True),
    Project("York", 20, 50),
    Project("Hull", 40, 60),
    Project("Bath", 10, 12),
]

print("bound at budget 85:", fractional_bound(refits, 85))
print("bound at budget 65:", fractional_bound(refits, 65))
print("bound at budget 25:", fractional_bound(refits, 25))
