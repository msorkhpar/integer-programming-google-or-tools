"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from checks import checks, required

snapshot = {
    "years": [2031, 2032],
    "budget": {2031: 300, 2032: 300},
    "crews": {"lines": {2031: 3, 2032: 3}, "poles": {2031: 2, 2032: 2}},
    "floor": {"East": 150, "West": 50},
    "projects": {
        "P1": {"program": "lines", "region": "East", "cost": [180], "earliest": 2031, "latest": 2032,
               "must": True, "group": None, "crews": 2},
        "P2": {"program": "poles", "region": "West", "cost": [90], "earliest": 2031, "latest": 2031,
               "must": False, "group": "A", "crews": 1},
        "P3": {"program": "poles", "region": "West", "cost": [70], "earliest": 2031, "latest": 2032,
               "must": True, "group": "A", "crews": 1},
    },
}

print("required, plain lock:", required(snapshot, {"name": "lock"}))
print("plain lock:", checks(snapshot, {"name": "lock"}))
print("P2 forced in:", checks(snapshot, {"name": "lock", "force_in": ["P2"]}))
print("budget 150 each year:", checks(snapshot, {"name": "lock", "budget": {2031: 150, 2032: 150}}))
print("P1 forced out, P3 fixed 2033:", checks(snapshot, {"name": "lock", "force_out": ["P1"], "fix_start": {"P3": 2033}}))
print("lines crews 1 in 2031 and 2032:", checks(snapshot, {"name": "lock", "crews": {"lines": {2031: 1, 2032: 1}}}))
