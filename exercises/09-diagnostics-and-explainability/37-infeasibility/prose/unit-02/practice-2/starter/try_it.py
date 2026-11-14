"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from cumulative import cumulative_check

money = {2030: 300, 2031: 300, 2032: 300}
jobs = {
    "valve-1": {"cost": 200, "deadline": 2030, "required": True},
    "valve-2": {"cost": 500, "deadline": 2031, "required": True},
    "mural": {"cost": 800, "deadline": 2030, "required": False},
    "tower": {"cost": 150, "deadline": 2032, "required": True},
}

print("short years, three jobs required:", cumulative_check(jobs, money))
jobs["valve-2"]["cost"] = 300
print("short years, valve-2 at 300:", cumulative_check(jobs, money))
print("short years, budget 100 a year:", cumulative_check(jobs, {2030: 100, 2031: 100, 2032: 100}))
