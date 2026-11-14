"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import copy
import json

from pydantic import ValidationError

from fleet import FleetSnapshot

clean = {
    "schema_version": 3, "horizon": [2031, 2032], "depots": ["East", "Quay"],
    "budgets": [{"year": 2031, "amount": 700}, {"year": 2032, "amount": 800}],
    "buses": [{"bus_id": "E1", "depot": "East", "cost": 390, "earliest": 2031, "latest": 2032},
              {"bus_id": "Q1", "depot": "Quay", "cost": 410, "earliest": 2032, "latest": 2032}],
}


def check(doc):
    try:
        FleetSnapshot.model_validate_json(json.dumps(doc))
        return "accepted"
    except ValidationError as error:
        return "; ".join(e["msg"] for e in error.errors())


bad = copy.deepcopy(clean)
bad["buses"][1]["depot"] = "Hill"
bad["budgets"].pop()
print("clean snapshot:", check(clean))
print("Q1 at Hill, no 2032 budget:", check(bad))
twice = copy.deepcopy(clean)
twice["buses"].append(dict(twice["buses"][0]))
print("E1 listed twice:", check(twice))
