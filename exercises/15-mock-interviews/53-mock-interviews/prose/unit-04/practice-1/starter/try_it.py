"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from filters import deletion_filter

clashes = [{"budget", "must_A", "must_B"}, {"crews", "must_C"}]
asked = []


def feasible(subset):
    asked.append(list(subset))
    return not any(clash <= set(subset) for clash in clashes)


print("rules crews, budget, must_A, must_B, must_C:",
      deletion_filter(["crews", "budget", "must_A", "must_B", "must_C"], feasible))
print("solves asked for:", len(asked))
print("rules must_C, must_B, must_A, budget, crews:",
      deletion_filter(["must_C", "must_B", "must_A", "budget", "crews"], feasible))
print("rules budget, must_A, crews:", deletion_filter(["budget", "must_A", "crews"], feasible))
