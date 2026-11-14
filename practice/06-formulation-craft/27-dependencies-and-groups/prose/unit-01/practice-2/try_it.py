"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from parks import Project, best_value, mandate_costs

# Park works: id, cost, value ($k); two are ordered by the safety inspector.
works = [
    Project("GATE", 4, 2, mandated=True),
    Project("RAIL", 3, 1, mandated=True),
    Project("POND", 7, 15),
    Project("PATH", 3, 4),
    Project("SIGN", 1, 2),
]

print("best value at budget 10, mandates kept:", best_value(works, 10, {"GATE", "RAIL"}))
print("best value at budget 10, nothing enforced:", best_value(works, 10, set()))
print("mandate costs at budget 10:", mandate_costs(works, 10))
print("mandate costs at budget 14:", mandate_costs(works, 14))
