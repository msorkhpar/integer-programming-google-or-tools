"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from sources import history

# Progress rows of a maximization run, in log order.
rows = [
    {"src": "z", "bound": float("inf"), "incumbent": 600.0},
    {"src": "J", "bound": 820.0, "incumbent": 740.0},
    {"src": "", "bound": 815.0, "incumbent": 740.0},
    {"src": "B", "bound": 810.0, "incumbent": 800.0},
]

found = history(rows)
print("lettered rows out of 4:", len(found))
for name, incumbent, gap in found:
    print("new incumbent:", name, incumbent, None if gap is None else round(gap, 4))
