"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from sweep import sweep

plans = [(7300, 210.0), (6900, 260.0), (6600, 300.0), (6000, 330.0)]   # (riders, tonnes cut)
asked = []


def solve_at(floor):
    asked.append(floor)
    meeting = [p for p in plans if p[1] >= floor - 1e-9]
    return max(meeting) if meeting else None


print("5 floors from 210 to 330:", sweep(solve_at, 210, 330, 5))
print("floors asked:", asked)
print("3 floors from 300 to 400:", sweep(solve_at, 300, 400, 3))
