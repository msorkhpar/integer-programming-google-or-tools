"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from guard import lock_refusal

plans = {
    "K-1": {"year": 2031, "state": "Reviewed", "inputs_hash": "f3",
            "run": {"inputs_hash": "f3", "status": "OPTIMAL"}},
    "K-2": {"year": 2031, "state": "Reviewed", "inputs_hash": "c9",
            "run": {"inputs_hash": "c2", "status": "OPTIMAL"}},
    "K-3": {"year": 2032, "state": "Submitted", "inputs_hash": "d4", "run": None},
    "K-4": {"year": 2033, "state": "Reviewed", "inputs_hash": "e5",
            "run": {"inputs_hash": "e5", "status": "FEASIBLE"}},
}
for plan_id in plans:
    print(f"lock {plan_id}:", lock_refusal(plan_id, plans))
plans["K-5"] = {"year": 2031, "state": "Locked", "inputs_hash": "a0", "run": None}
print("lock K-1 with K-5 Locked for 2031:", lock_refusal("K-1", plans))
