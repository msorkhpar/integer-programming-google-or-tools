"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from gas_plan import diff_scenarios

autumn = {"name": "autumn", "plan": [
    {"id": "GM-1", "start": "2030-Q2"},
    {"id": "GM-4", "start": "2030-Q4"},
    {"id": "GM-7", "start": "2031-Q1"},
]}
winter = {"name": "winter", "plan": [
    {"id": "GM-7", "start": "2030-Q3"},
    {"id": "GM-4", "start": "2031-Q2"},
    {"id": "GM-9", "start": "2030-Q1"},
]}

d = diff_scenarios(autumn, winter)
print("adds, autumn to winter:", d["adds"])
print("drops, autumn to winter:", d["drops"])
for s in d["shifts"]:
    print(f"shift of {s['id']}:", s)
