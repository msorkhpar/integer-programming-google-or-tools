"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import copy

from cross import cross_checks

clean = {
    "crews": {"paving": 10, "drainage": 6},
    "jobs": [
        {"id": "R1", "crew": "paving", "crew_weeks": 6, "required": True, "after": None, "exclusive": None},
        {"id": "R2", "crew": "paving", "crew_weeks": 3, "required": False, "after": None, "exclusive": "K1"},
        {"id": "R3", "crew": "paving", "crew_weeks": 2, "required": False, "after": None, "exclusive": "K1"},
        {"id": "D1", "crew": "drainage", "crew_weeks": 4, "required": False, "after": "R2", "exclusive": None},
    ],
}
both = copy.deepcopy(clean)
both["jobs"][2]["required"] = True
both["jobs"][3]["required"] = True

print("clean snapshot:", cross_checks(clean))
print("D1 and R3 required:", cross_checks(both))
one = copy.deepcopy(clean)
one["jobs"][2]["required"] = True
print("R3 required:", cross_checks(one))
one["jobs"][0]["crew_weeks"] = 9
print("R3 required, R1 at 9 weeks:", cross_checks(one))
