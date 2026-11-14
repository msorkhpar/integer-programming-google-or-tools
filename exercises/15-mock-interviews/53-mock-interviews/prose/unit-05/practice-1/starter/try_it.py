"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
import copy

from snapshots import snapshot_digest

snapshot = {
    "scenario": "storm-season",
    "budgets": {"2031": 700, "2032": 640},
    "projects": [{"pid": "W2", "cost": 220}, {"pid": "W1", "cost": 310}],
    "must_do": ["W2", "W1"],
}
shuffled = {"must_do": ["W1", "W2"], "projects": [{"cost": 310, "pid": "W1"}, {"pid": "W2", "cost": 220}],
            "budgets": {"2032": 640, "2031": 700}, "scenario": "storm-season"}
changed = copy.deepcopy(snapshot)
changed["budgets"]["2032"] = 641

print("storm-season digest:", snapshot_digest(snapshot))
print("same content reordered:", snapshot_digest(shuffled))
print("2032 budget 641:", snapshot_digest(changed))
