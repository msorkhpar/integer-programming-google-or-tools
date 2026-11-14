"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from count import Project, count_allowed

# Five lift refits; L1 is ordered by the inspector.
lifts = [
    Project("L1", 30, must_do=True),
    Project("L2", 25),
    Project("L3", 20, parent="L2"),
    Project("L4", 15, group="doors"),
    Project("L5", 10, group="doors"),
]
for budget in (30, 60, 100):
    print(f"allowed plans at budget {budget}:", count_allowed(lifts, budget))
