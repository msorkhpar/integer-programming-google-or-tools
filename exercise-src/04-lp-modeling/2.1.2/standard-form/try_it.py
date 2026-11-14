"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from standard_form import standard_form

variables = ["bricks", "tiles", "slabs"]
rows = [
    ({"bricks": 3, "tiles": 1}, "<=", 60),
    ({"tiles": 1, "slabs": 1}, ">=", 8),
    ({"bricks": 1, "slabs": -2}, "==", 5),
]
c, A, b = standard_form(variables, {"bricks": 4, "tiles": 2, "slabs": 1}, "min", rows)
print("c:", c)
print("A:", A)
print("b:", b)
