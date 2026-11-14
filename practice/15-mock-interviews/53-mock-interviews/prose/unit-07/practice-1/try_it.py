"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from costs import Project, decision_costs

# A bus company's depot works.
works = [
    Project("Roof", 45, 25),
    Project("Wash", 35, 20),
    Project("Pits", 30, 25),
    Project("Fence", 8, 10, must_do=True),
]

for budget in (55, 70, 10):
    costs = decision_costs(works, budget)
    print(f"budget {budget}:", {pid: None if c is None else round(c, 2) for pid, c in costs.items()})
