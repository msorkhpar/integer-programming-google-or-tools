"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from audit import audit

run = {"snapshot": "c41e", "settings": {"threads": 2, "gap": 0.0}, "status": "OPTIMAL",
       "objective": 1450.5, "plan": {"P2": 2031, "P6": 2032}}

print("same run:", audit(run, {**run, "plan": dict(run["plan"])}))
print("gap 0.01, objective 1449:", audit(run, {**run, "settings": {"threads": 2, "gap": 0.01},
                                                 "objective": 1449.0}))
print("P6 in 2033:", audit(run, {**run, "plan": {"P2": 2031, "P6": 2033}}))
print("snapshot d002:", audit(run, {**run, "snapshot": "d002", "objective": 900.0}))
