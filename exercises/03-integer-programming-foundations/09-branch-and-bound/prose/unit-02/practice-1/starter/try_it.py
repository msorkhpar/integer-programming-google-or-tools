"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from classify import classify

print("infeasible node, incumbent 120:", classify("infeasible", 0.0, False, 120.0))
print("bound 131.5 fractional, incumbent 120:", classify("optimal", 131.5, False, 120.0))
print("bound 125 integral, incumbent 120:", classify("optimal", 125.0, True, 120.0))
print("bound 118 fractional, incumbent 120:", classify("optimal", 118.0, False, 120.0))
print("bound 120.8 fractional, incumbent 120, whole values:", classify("optimal", 120.8, False, 120.0, whole_values=True))
print("bound 40.5 fractional, no incumbent:", classify("optimal", 40.5, False, None))
