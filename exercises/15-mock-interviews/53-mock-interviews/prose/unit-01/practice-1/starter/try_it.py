"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from lags import start_to_start, usable_child_years

for kind, lag, parent_d, child_d in (("SS", 1, 2, 2), ("FS", 0, 2, 3), ("FF", 1, 3, 2), ("SF", 3, 2, 1)):
    print(f"{kind} lag {lag}, parent {parent_d} years, child {child_d} years:",
          start_to_start(kind, lag, parent_d, child_d))

print("parent (2030, 2032), child (2030, 2031, 2033, 2034), lag 2:",
      usable_child_years((2030, 2032), (2030, 2031, 2033, 2034), 2))
print("parent (2031,), child (2029, 2030, 2031), lag 0:", usable_child_years((2031,), (2029, 2030, 2031), 0))
