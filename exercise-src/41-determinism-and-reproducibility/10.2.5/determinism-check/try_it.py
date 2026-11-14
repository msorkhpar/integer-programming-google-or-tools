"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from determinism import assert_deterministic


def steady():
    return {"status": "OPTIMAL", "objective": 31.0, "plan": [["D1", "z2"], ["D2", "z1"]]}


calls = []


def drifting():
    calls.append(1)
    plan = [["D1", "z2"], ["D2", "z1"]] if len(calls) < 3 else [["D1", "z1"], ["D2", "z2"]]
    return {"status": "OPTIMAL", "objective": 31.0, "plan": plan}


print("digest of 4 steady runs:", assert_deterministic(steady, 4))
try:
    print("digest of 4 drifting runs:", assert_deterministic(drifting, 4))
except AssertionError as error:
    print("4 drifting runs refused:", error)
