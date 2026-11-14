"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from certify import certify

# A joinery's week: tables, chairs and shelves, profit per batch.
value = {"tables": 5, "chairs": 3, "shelves": 2}
rows = {
    "saw": ({"tables": 2, "chairs": 1, "shelves": 1}, "<=", 14),
    "glue": ({"tables": 1, "chairs": 1}, "<=", 8),
}
print("plan tables 6, chairs 2, shelves 0:", certify(value, rows, {"tables": 6, "chairs": 2, "shelves": 0}))
print("plan tables 7, chairs 0, shelves 0:", certify(value, rows, {"tables": 7, "chairs": 0, "shelves": 0}))
