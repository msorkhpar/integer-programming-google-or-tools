"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from manifest_diff import diff_paths

run = {"inputs": {"snapshot": "c9d0", "line": "east"},
       "result": {"status": "OPTIMAL", "objective": 58.0, "plan": [["J2", 1], ["J5", 3]]}}
rerun = {"inputs": {"snapshot": "c9d0", "line": "east"},
         "result": {"status": "OPTIMAL", "objective": 57.0, "plan": [["J2", 2], ["J5", 3]], "gap": 0.0}}

print("paths, run vs itself:", diff_paths(run, run))
print("paths, run vs rerun:", diff_paths(run, rerun))
print("paths, plan of three vs two:",
      diff_paths(run, {**run, "result": {**run["result"], "plan": [["J2", 1], ["J5", 3], ["J8", 2]]}}))
