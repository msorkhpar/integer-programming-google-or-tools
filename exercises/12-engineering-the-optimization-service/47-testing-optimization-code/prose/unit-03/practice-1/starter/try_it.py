"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from roster_golden import compare

golden = {"status": "OPTIMAL", "cost": 860.0, "assign": {"k1": "green", "k2": "gold"},
          "overtime": {"green": 1.5, "gold": 0.0}}

print("identical record:", compare(golden, dict(golden)))
print("cost 860.3, gold overtime 0.003:", compare(golden, {**golden, "cost": 860.3, "overtime": {"green": 1.5, "gold": 0.003}}))
print("cost 905, k2 to green, k5 added:",
      compare(golden, {**golden, "cost": 905.0, "assign": {"k1": "green", "k2": "green", "k5": "gold"}}))
print("status INFEASIBLE:", compare(golden, {**golden, "status": "INFEASIBLE", "cost": 0.0}))
