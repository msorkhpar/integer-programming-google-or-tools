"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
import math

from breakpoints import fewest_breakpoints

print("x^3 on [0, 1], tol 0.02:", fewest_breakpoints(lambda x: x ** 3, 0.0, 1.0, 0.02))
print("x^3 on [0, 1], tol 0.002:", fewest_breakpoints(lambda x: x ** 3, 0.0, 1.0, 0.002))
print("exp on [0, 2], tol 0.05:", fewest_breakpoints(math.exp, 0.0, 2.0, 0.05))
print("line 2x + 1 on [0, 4], tol 0.001:", fewest_breakpoints(lambda x: 2 * x + 1, 0.0, 4.0, 0.001))
print("exp on [0, 2], tol 1e-6, max_n 10:", fewest_breakpoints(math.exp, 0.0, 2.0, 1e-6, max_n=10))
