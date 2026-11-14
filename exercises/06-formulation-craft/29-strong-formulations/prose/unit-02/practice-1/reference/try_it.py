"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from inspections import tighten

# Four site visits: cost, and hours each gives to two districts.
cost = {"P": 3, "Q": 6, "R": 2, "T": 1}
hours = {"valley": {"P": 4, "Q": 2, "R": 1}, "ridge": {"Q": 3, "R": 2, "T": 2}}

ones, zeros = tighten(cost, 7, hours, {"valley": 5, "ridge": 3})
print("budget 7, fixed at 1:", sorted(ones))
print("budget 7, fixed at 0:", sorted(zeros))
ones, zeros = tighten(cost, 12, hours, {"valley": 2, "ridge": 1})
print("budget 12, fixed at 1:", sorted(ones))
print("budget 12, fixed at 0:", sorted(zeros))
