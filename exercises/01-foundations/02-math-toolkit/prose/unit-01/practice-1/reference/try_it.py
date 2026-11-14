"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import numpy as np

from check import broken_rows, is_feasible

# Two machines share three jobs; rows are machine-hours, columns are jobs.
A = np.array([[2, 3, 1],
              [1, 0, 4]])
b = np.array([10, 6])

for x in ([1, 2, 1], [2, 1, 1], [3, 2, 1]):
    x = np.array(x)
    print(f"plan {x.tolist()}: broken rows", broken_rows(A, b, x), "feasible", is_feasible(A, b, x))
