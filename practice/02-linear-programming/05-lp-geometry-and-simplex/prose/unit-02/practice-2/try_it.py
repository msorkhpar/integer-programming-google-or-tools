"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from pivot import pivot

T = [[2, 1, 1, 0, 0, 10],
     [1, 2, 0, 1, 0, 8],
     [0, 1, 0, 0, 1, 3],
     [-4, -5, 0, 0, 0, 0]]
after = pivot(T, 2, 1)
for i, row in enumerate(after):
    print(f"row {i} after pivot (2, 1):", [round(v, 4) for v in row])
print("row 3 of T itself:", T[3])
