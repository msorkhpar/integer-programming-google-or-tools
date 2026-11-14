"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from simplex import run_simplex

T = [[2, 1, 1, 0, 0, 10],
     [1, 2, 0, 1, 0, 8],
     [0, 1, 0, 0, 1, 3],
     [-4, -5, 0, 0, 0, 0]]
print("tableau with three rows:", run_simplex(T))
open_side = [[-1, 2, 1, 4],
             [-3, -1, 0, 0]]
print("tableau with column 0 all negative:", run_simplex(open_side))
