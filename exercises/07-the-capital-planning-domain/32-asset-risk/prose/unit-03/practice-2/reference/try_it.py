"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from register import Valve, rank_by_risk, risk

valves = [Valve("North", 25, 3.0, 45, 500), Valve("Harbor", 25, 3.0, 45, 1_100),
          Valve("Mill", 55, 3.0, 45, 400), Valve("Ridge", 8, 3.0, 45, 3_000)]

for v in valves:
    print(f"{v.valve_id} age {v.age}, cof {v.cof}:", round(risk(v), 3))
print("ranked:", rank_by_risk(valves))
