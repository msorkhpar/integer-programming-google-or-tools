"""One result, the 2029 budget cut, written for planners, finance and auditors from one record (lesson 9.3.4)."""

import json

from gridcap import generate

from explain_model import Scenario
from record import for_auditors, for_finance, for_planners, make_record

small = generate("small")
record = make_record(small, Scenario("base"), Scenario("cut-2029", budget={2029: 6000}))

keys = ("scenario", "status", "npv", "bound", "selected", "deferred", "inputs_changed")
print("RECORD (some of its fields)")
print(json.dumps({k: record[k] for k in keys}))
print("  reasons P005:", json.dumps(record["reasons"]["P005"]))
for title, writer in (("PLANNERS", for_planners), ("FINANCE", for_finance), ("AUDITORS", for_auditors)):
    print()
    print(title)
    for line in writer(record):
        print(line)
