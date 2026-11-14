"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from water_properties import must_dos_funded, prerequisites_funded, within_both_budgets

instance = {"cost": {"v1": (25, 3), "v2": (15, 2), "v3": (30, 4)}, "budget": (50, 6), "must": ["v1"],
            "needs": {"v1": [], "v2": ["v1"], "v3": ["v2"]}, "value": {"v1": 6, "v2": 3, "v3": 8}}


def holds(prop, plan):
    try:
        prop(instance, plan)
        return "holds"
    except AssertionError:
        return "fails"


for plan in ({"v1", "v2"}, {"v2"}, {"v1", "v3"}, {"v1", "v2", "v3"}):
    print(f"plan {sorted(plan)}: budgets {holds(within_both_budgets, plan)}, "
          f"must-dos {holds(must_dos_funded, plan)}, prerequisites {holds(prerequisites_funded, plan)}")
