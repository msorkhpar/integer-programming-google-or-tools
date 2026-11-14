"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from snapshot import snapshot

plan = {"id": "Q-3", "name": "winter", "owner": "planner-x",
        "demand": {"harbour": 25, "airport": 18}, "budget": {2030: 600, 2031: 640},
        "settings": {"solver": "HIGHS", "gap": 0.02}}
renamed = {**plan, "id": "Q-9", "name": "winter copy", "owner": "planner-y"}
reordered = {**plan, "demand": {"airport": 18, "harbour": 25}}
tighter = {**plan, "settings": {"solver": "HIGHS", "gap": 0.0}}

print("Q-3:          ", snapshot(plan))
print("renamed Q-9:  ", snapshot(renamed))
print("demand reordered:", snapshot(reordered))
print("gap 0.0:      ", snapshot(tighter))
