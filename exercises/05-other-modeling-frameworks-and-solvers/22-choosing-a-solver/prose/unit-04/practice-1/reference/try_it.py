"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from claim import faster

# Wall seconds per repetition for two solvers on a depot-routing benchmark.
fast = [0.8, 0.7, 0.9, 0.75]
slow = [2.5, 2.2, 3.1, 2.4]
mixed = [1.4, 0.6, 2.0, 1.6]

print("fast vs slow at factor 2.5:", faster(fast, slow, 2.5))
print("fast vs slow at factor 3.5:", faster(fast, slow, 3.5))
print("slow vs fast at factor 2.5:", faster(slow, fast, 2.5))
print("fast vs mixed at factor 1.5:", faster(fast, mixed, 1.5))
