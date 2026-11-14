"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from leaks import exact_sweep

frontier = [(610.0, 50), (640.0, 54), (655.0, 61), (700.0, 70)]   # (leak cut, cost)
asked = []


def solve_at(ceiling):
    asked.append(ceiling)
    within = [p for p in frontier if p[1] <= ceiling]
    if not within:
        return None
    best = max(within)
    return best, ceiling - best[1]


print("ceilings 45 to 72:", exact_sweep(solve_at, 45, 72))
print("ceilings asked:", asked)
