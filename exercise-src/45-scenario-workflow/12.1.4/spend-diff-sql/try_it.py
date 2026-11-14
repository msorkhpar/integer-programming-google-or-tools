"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import sqlite3

from spend import SCHEMA, spend_diff

conn = sqlite3.connect(":memory:")
conn.executescript(SCHEMA)
conn.executemany("INSERT INTO cost VALUES (?, ?, ?)",
                 [("R-1", 0, 100), ("R-1", 1, 60), ("R-2", 0, 80), ("R-3", 0, 120)])
conn.executemany("INSERT INTO run_start VALUES (?, ?, ?)", [
    (7, "R-1", 2031), (7, "R-2", 2032),
    (8, "R-1", 2032), (8, "R-2", 2032), (8, "R-3", 2034),
])
print("run 7 vs run 8:", spend_diff(conn, 7, 8))
print("run 8 vs run 7:", spend_diff(conn, 8, 7))
print("run 7 vs itself:", spend_diff(conn, 7, 7))
