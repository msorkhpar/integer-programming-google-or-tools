"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import copy

from review import rejected, review

clean = {
    "horizon": [2031, 2032, 2033],
    "budgets": {2031: 800, 2032: 800, 2033: 800},
    "jobs": [
        {"id": "P1", "cost": [400], "earliest": 2031, "latest": 2032, "required": True, "after": None, "lag": 0},
        {"id": "P2", "cost": [300], "earliest": 2032, "latest": 2033, "required": False, "after": "P1", "lag": 1},
        {"id": "P3", "cost": [200], "earliest": 2031, "latest": 2033, "required": False, "after": None, "lag": 0},
    ],
}
dirty = copy.deepcopy(clean)
dirty["jobs"][1]["lag"] = 5
dirty["jobs"][2]["after"] = "P3"
dirty["budgets"][2033] = 100

print("clean snapshot:", review(clean, clean), "rejected:", rejected(review(clean, clean)))
for finding in review(dirty, clean):
    print("dirty snapshot finding:", finding)
print("dirty snapshot rejected:", rejected(review(dirty, clean)))
