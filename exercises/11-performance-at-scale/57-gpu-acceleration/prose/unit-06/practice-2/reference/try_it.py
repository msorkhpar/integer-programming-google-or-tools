"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from answers import usable

print("bound, gpu 5300.0, cpu 5300.002:", usable("bound", {"status": "Optimal", "objective": 5300.0}, {"objective": 5300.002}))
print("bound, gpu 5300.0, cpu 5310.0:", usable("bound", {"status": "Optimal", "objective": 5300.0}, {"objective": 5310.0}))
print("bound, gpu status TimeLimit:", usable("bound", {"status": "TimeLimit", "objective": 5300.0}, {"objective": 5300.0}))
print("start, checked feasible and integral:", usable("start", {"status": "FeasibleFound", "x": [0, 1, 1]},
                                                      {"feasible": True, "integral": True}))
print("start, not integral:", usable("start", {"status": "Optimal", "x": [0, 0.5, 1]}, {"feasible": True, "integral": False}))
print("plan:", usable("plan", {"status": "Optimal", "objective": 5300.0, "x": [0, 1, 1]},
                      {"objective": 5300.0, "feasible": True, "integral": True}))
