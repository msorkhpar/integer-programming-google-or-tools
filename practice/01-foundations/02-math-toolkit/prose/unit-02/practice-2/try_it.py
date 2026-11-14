"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from activity import csr_activity

#   row 0: 3 x1 + 2 x2
#   row 1: (empty)
#   row 2: 1 x0 + 6 x2
indptr = [0, 2, 2, 4]
indices = [1, 2, 0, 2]
data = [3.0, 2.0, 1.0, 6.0]

print("activity at x = [1, 1, 1]:", csr_activity(indptr, indices, data, [1.0, 1.0, 1.0]))
print("activity at x = [4, 2, 0.5]:", csr_activity(indptr, indices, data, [4.0, 2.0, 0.5]))
