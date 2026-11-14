"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from refusals import Limit, full_but_not_tight, refusals

limits = [
    Limit("works_fund", {"bridge": 250, "tunnel": 300, "lights": 80, "kerbs": 40}, 600),
    Limit("crew_months", {"bridge": 5, "tunnel": 6, "lights": 2, "kerbs": 1}, 10),
    Limit("one_big_job", {"bridge": 1, "tunnel": 1}, 1),
]
plan = {"bridge", "lights"}

for job, broken in refusals(limits, plan, ["tunnel", "kerbs"]).items():
    print(f"limits broken by adding {job}:", broken)
print("limits with room that refuse tunnel:", full_but_not_tight(limits, plan, ["tunnel"]))
