"""Lesson 12.1.1: a scenario is a record of inputs; its snapshot covers the inputs and nothing else.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.
The people (`planner-a`, ...) are placeholders.
"""

import json
from dataclasses import replace

from gridcap import generate
from scenario import DataRef, Scenario, create, load_portfolio

small = generate("small")
clock_times = iter(["2027-03-01T09:00Z", "2027-03-01T09:05Z"])

base = create(small, "small", "S-001", "base", by="planner-a", at=next(clock_times))
record = json.loads(base.to_json())
print("record keys:", sorted(record))
print("inputs keys:", sorted(base.inputs()))
print("budget:", record["budget"])
print("snapshot:", base.snapshot()[:12])

# Metadata is not an input: renaming the scenario or changing who made it keeps the snapshot.
renamed = replace(base, name="base (reviewed)", created_by="planner-b", created_at=next(clock_times))
print("renamed, same snapshot:", renamed.snapshot() == base.snapshot())
# An input is: one budget changed by $1k gives another snapshot.
nudged = replace(base, budget={**base.budget, 2030: base.budget[2030] - 1})
print("budget 2030 less $1k, same snapshot:", nudged.snapshot() == base.snapshot())

# The scenario names its data by hash, so data that changed underneath it is refused.
try:
    load_portfolio(DataRef("small", small.seed + 1, base.data.content_hash))
except ValueError as e:
    print("refused:", e)

# JSON turns the integer year keys into strings; from_json turns them back.
raw = json.loads(base.to_json())["budget"]
print("json.loads keys:", list(raw)[:2], " 2030 in it:", 2030 in raw)
again = Scenario.from_json(base.to_json())
print("round trip equal:", again == base, " same snapshot:", again.snapshot() == base.snapshot())
