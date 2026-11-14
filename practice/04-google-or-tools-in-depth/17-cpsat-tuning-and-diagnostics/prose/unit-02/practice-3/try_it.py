"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from depot_rules import Rule, minimal_clash

# Crew counts (low, high) for three depots.
crews = {"quay": (0, 5), "mill": (0, 5), "fort": (0, 5)}
all_cap = Rule("all_cap", {"quay": 1, "mill": 1, "fort": 1}, "<=", 12)
mill_max = Rule("mill_max", {"mill": 1}, "<=", 1)
mill_min = Rule("mill_min", {"mill": 1}, ">=", 3)
pair = Rule("quay_fort_min", {"quay": 1, "fort": 1}, ">=", 6)
print("all_cap, quay_fort_min, mill_max, mill_min:", minimal_clash(crews, [all_cap, pair, mill_max, mill_min]))
print("all_cap, quay_fort_min, mill_max:", minimal_clash(crews, [all_cap, pair, mill_max]))
print("all_cap at 5 with quay_fort_min, mill_min:",
      minimal_clash(crews, [Rule("all_cap", all_cap.terms, "<=", 5), pair, mill_min]))
