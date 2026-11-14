"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from leq import to_leq

# A kitchen orders three ingredients; x[j] is how many crates of ingredient j.
rules = [
    ({0: 3, 1: 2, 2: 1}, "<=", 30),   # fridge space
    ({0: 1, 2: 1}, ">=", 4),          # at least 4 crates of ingredients 0 and 2
    ({1: 1}, "==", 2),                # exactly 2 crates of ingredient 1
]
A, b = to_leq(rules, 3)
print("A rows:", A.tolist())
print("b:", b.tolist())
