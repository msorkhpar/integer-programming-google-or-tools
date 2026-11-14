"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from crew import build, solve

values = [6.0, 10.0, 7.0, 4.0, 9.0]
hours = [[3, 0], [2, 4], [0, 3], [1, 1], [4, 2]]
capacity = [6.0, 6.0]
requires = [(0, 3)]

lp = build(values, hours, capacity, requires)
print("rows:", lp.num_row_, "columns:", lp.num_col_)
status, value, x = solve(lp)
print("best selection:", status, value, [round(v) for v in x])
status, value, x = solve(lp, fixed={3: 1})
print("job 3 pinned to 1:", status, value, [round(v) for v in x])
status, value, x = solve(lp, fixed={3: 1, 0: 0})
print("job 3 pinned to 1, job 0 to 0:", status)
print("a second run gives the same answer:", solve(lp) == solve(lp))
