"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from pivots import choose_pivot

T = [[2, 1, 1, 0, 0, 10],
     [1, 2, 0, 1, 0, 8],
     [0, 1, 0, 0, 1, 3],
     [-4, -5, 0, 0, 0, 0]]
print("pivot of T:", choose_pivot(T))
done = [[1, 0, 1, 0, 2],
        [0, 1, 0, 1, 3],
        [0, 0, 1, 2, 9]]
print("pivot of a tableau with no negative cost:", choose_pivot(done))
