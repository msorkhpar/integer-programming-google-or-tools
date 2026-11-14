"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from sgm import shifted_geometric_mean

times = [0.2, 3.0, 45.0, 600.0]
print("times", times, "shift 0:", round(shifted_geometric_mean(times, 0.0), 3))
print("times", times, "shift 10:", round(shifted_geometric_mean(times, 10.0), 3))
print("times [5, 5, 5], shift 10:", round(shifted_geometric_mean([5.0, 5.0, 5.0], 10.0), 3))
print("times [0.05, 0.5], shift 0:", round(shifted_geometric_mean([0.05, 0.5], 0.0), 3))
