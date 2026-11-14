"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from audit import leaks

# Two crane rules, each switched off by its own permit variable.
rows = [{"name": "crane_east", "terms": {"lift_a": 3, "lift_b": 2}, "limit": 4, "switch": "permit_e"},
        {"name": "crane_west", "terms": {"lift_c": 6}, "limit": 6, "switch": "permit_w"}]

print("permits 1e-8 and 1:", leaks({"lift_a": 1, "lift_b": 1, "lift_c": 2, "permit_e": 1e-8, "permit_w": 1}, rows))
print("permits 0.3 and 0.2:", leaks({"lift_a": 1, "lift_b": 1, "lift_c": 2, "permit_e": 0.3, "permit_w": 0.2}, rows))
print("permits 1 and 0, lift_c 1:", leaks({"lift_a": 1, "lift_b": 1, "lift_c": 1, "permit_e": 1, "permit_w": 0}, rows))
