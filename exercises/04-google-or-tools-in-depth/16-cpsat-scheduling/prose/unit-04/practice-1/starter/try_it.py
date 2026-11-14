"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from workshop import least_penalty

# Each repair is (days, mechanics, due day, penalty per late day).
jobs = {"gearbox": (3, 2, 3, 4), "brakes": (2, 1, 2, 7), "clutch": (2, 1, 5, 2)}
for mechanics in (3, 2):
    total, start = least_penalty(jobs, mechanics, 15)
    print(f"{mechanics} mechanics: penalty {total}, starts {start}")
