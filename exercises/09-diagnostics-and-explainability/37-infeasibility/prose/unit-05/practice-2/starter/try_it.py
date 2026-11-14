"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from families import two_pass

families = {
    "pumps": ["pump_P1", "pump_P2"],
    "quiet": ["quiet_nights"],
    "money": ["money_h1", "money_h2"],
    "crew": ["crew_min_2"],
}


def oracle(*clashes):
    sets = [set(c) for c in clashes]
    return lambda on: any(c <= set(on) for c in sets)


print("families and rules, pump_P1 vs money_h2:", two_pass(families, oracle(["pump_P1", "money_h2"])))
print("families and rules, quiet_nights vs crew_min_2:", two_pass(families, oracle(["quiet_nights", "crew_min_2"])))
