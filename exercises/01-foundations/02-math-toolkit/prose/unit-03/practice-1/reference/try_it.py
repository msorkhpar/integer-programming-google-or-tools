"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import numpy as np

from extreme import is_extreme_point

# A tank farm: x0 litres of diesel and x1 of petrol (thousands).
#   x0 <= 5, x1 <= 4, x0 + x1 <= 7, x0 >= 0, x1 >= 0
A = np.array([[1, 0], [0, 1], [1, 1], [-1, 0], [0, -1]])
b = np.array([5, 4, 7, 0, 0])

for x in ([5, 2], [3, 4], [1, 1], [5, 1], [0, 0], [5, 4]):
    print(f"point {x}:", is_extreme_point(A, b, np.array(x)))
