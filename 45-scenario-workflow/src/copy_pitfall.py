"""Lesson 12.1.1: a shallow copy shares the budget with its parent; copy_scenario shares nothing mutable.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.
"""

import copy

from gridcap import generate
from scenario import copy_scenario, create

small = generate("small")
base = create(small, "small", "S-001", "base", by="planner-a", at="2027-03-01T09:00Z")
before = base.snapshot()

shallow = copy.copy(base)
shallow.scenario_id, shallow.name = "S-002", "cut-2030"
shallow.budget[2030] = 7750
print("shallow copy: base budget 2030 is now", base.budget[2030], "| base snapshot changed:", base.snapshot() != before)
print("  same dict object:", shallow.budget is base.budget)

base = create(small, "small", "S-001", "base", by="planner-a", at="2027-03-01T09:00Z")
cut = copy_scenario(base, "S-002", "cut-2030", by="planner-b", at="2027-03-01T09:10Z")
print("copy_scenario: parent", cut.parent_id, "| same snapshot as base:", cut.snapshot() == base.snapshot())
cut.budget[2030] = 7750
print("  after the edit: base budget 2030", base.budget[2030], "| cut", cut.budget[2030],
      "| base snapshot changed:", base.snapshot() != before)
