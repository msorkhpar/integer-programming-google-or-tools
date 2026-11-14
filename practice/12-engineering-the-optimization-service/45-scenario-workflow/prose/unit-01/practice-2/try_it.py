"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from plan import Plan, copy_plan

base = Plan("P-10", "spring", {2030: 500, 2031: 540}, {"east": [2, 2, 3], "west": [1, 1, 1]},
            created_by="planner-x", tags=["review"])
trial = copy_plan(base, "P-11", "dry summer", "planner-y")
trial.budget[2031] = 400
trial.crews["east"][0] = 5
trial.tags.append("what-if")

print("copy:", trial.plan_id, trial.name, trial.created_by, "parent", trial.parent_id)
print("budget  base:", base.budget, " copy:", trial.budget)
print("east crews  base:", base.crews["east"], " copy:", trial.crews["east"])
print("tags  base:", base.tags, " copy:", trial.tags)
