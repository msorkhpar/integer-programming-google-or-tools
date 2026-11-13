"""Lesson 7.1.2: which of the model's rules each fleet's projects bring with them.

GridCap is a fictional utility's portfolio, generated for this course; no number in it is real.
"""

from collections import Counter

from gridcap import PROGRAMS, generate

small = generate("small")

rules: dict[str, Counter] = {prog: Counter() for prog in PROGRAMS}
for p in small.projects:
    tally = rules[p.program]
    tally["must-do"] += p.must_do
    tally["alternative"] += p.alt_group is not None
    tally["has parent"] += p.parent is not None
    tally["is parent"] += any(c.parent == p.project_id for c in small.projects)
    tally["multi-year spend"] += p.duration > 1
    tally["several start years"] += p.latest_start > p.earliest_start

kinds = ["must-do", "alternative", "has parent", "is parent", "multi-year spend", "several start years"]
print(f"{'program':14}" + "".join(f"{k:>21}" for k in kinds))
for prog in PROGRAMS:
    print(f"{prog:14}" + "".join(f"{rules[prog][k]:>21}" for k in kinds))
