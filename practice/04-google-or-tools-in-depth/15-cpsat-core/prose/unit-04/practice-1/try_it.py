"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from twins import best_with_cpsat, best_with_highs

# Park improvements: value points and cost in $k.
value = {"bench": 3, "trail": 8, "pond": 6, "kiosk": 5, "swing": 4}
cost = {"bench": 10, "trail": 35, "pond": 30, "kiosk": 25, "swing": 20}
requires = [("kiosk", "trail")]
excludes = [("pond", "swing")]

for budget in (50, 80):
    print(f"budget {budget}, rules on, CP-SAT:", best_with_cpsat(value, cost, budget, requires, excludes))
    print(f"budget {budget}, rules on, HiGHS:", best_with_highs(value, cost, budget, requires, excludes))
print("budget 80, no rules, CP-SAT:", best_with_cpsat(value, cost, 80, [], []))
