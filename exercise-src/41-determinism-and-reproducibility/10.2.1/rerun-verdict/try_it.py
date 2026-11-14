"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from verdict import verdict

run = {"status": "OPTIMAL", "objective": 64.0, "plan": {"K1": "R3", "K2": "R1", "K3": "R2"}}

print("same run again:", verdict(run, dict(run)))
print("K1 and K2 swap rooms:", verdict(run, {**run, "plan": {"K1": "R1", "K2": "R3", "K3": "R2"}}))
print("objective 64.0000000002:", verdict(run, {**run, "objective": 64.0000000002}))
print("objective 61:", verdict(run, {**run, "objective": 61.0}))
print("status FEASIBLE:", verdict(run, {**run, "status": "FEASIBLE"}))
