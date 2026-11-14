"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import json

from contract import parse

v3 = {"schema_version": 3, "buses": [
    {"bus_id": "C11", "depot": "East", "cost": 510, "must_replace": False},
    {"bus_id": "C12", "depot": "West", "cost": 530, "must_replace": True}]}
v2 = {"schema_version": 2, "buses": [{"bus_id": "C21", "garage": "East", "cost": 280}]}
cost_as_text = {**v3, "buses": [{**v3["buses"][0], "cost": "510"}]}
v2_with_flag = {**v2, "buses": [{**v2["buses"][0], "must_replace": True}]}

print("version 3:", parse(json.dumps(v3)))
print("version 2:", parse(json.dumps(v2)))
print("cost sent as text:", parse(json.dumps(cost_as_text)))
print("version 2 with must_replace:", parse(json.dumps(v2_with_flag)))
