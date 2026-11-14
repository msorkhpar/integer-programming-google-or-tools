"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from triage import classify

golden = {"input": "a71e", "status": "OPTIMAL", "cost": 1430.0, "assign": {"k1": "green", "k2": "gold"}}

print("identical record:", classify(golden, dict(golden)))
print("cost 1390:", classify(golden, {**golden, "cost": 1390.0}))
print("cost 1475:", classify(golden, {**golden, "cost": 1475.0}))
print("cost 1430.4, crews swapped:", classify(golden, {**golden, "cost": 1430.4, "assign": {"k1": "gold", "k2": "green"}}))
print("status TIME_LIMIT:", classify(golden, {**golden, "status": "TIME_LIMIT"}))
print("input 3c09, status TIME_LIMIT:", classify(golden, {**golden, "input": "3c09", "status": "TIME_LIMIT"}))
