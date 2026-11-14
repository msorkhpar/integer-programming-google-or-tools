"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from crew_rules import Rule, clashing_rules

# Crew counts (low, high) for three depots.
crews = {"quay": (3, 5), "mill": (0, 4), "fort": (1, 4)}
rules = [
    Rule("all_cap", {"quay": 1, "mill": 1, "fort": 1}, "<=", 8),
    Rule("quay_fort_cap", {"quay": 1, "fort": 1}, "<=", 3),
    Rule("mill_min", {"mill": 1}, ">=", 2),
]
print("all three rules:", clashing_rules(crews, rules))
print("without quay_fort_cap:", clashing_rules(crews, [rules[0], rules[2]]))
print("with mill_min raised to 6:", clashing_rules(crews, [rules[0], Rule("mill_min", {"mill": 1}, ">=", 6)]))
