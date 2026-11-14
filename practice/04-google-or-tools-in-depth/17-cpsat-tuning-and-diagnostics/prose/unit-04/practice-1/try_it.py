"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from log_sizes import variables_before_and_after

# A made-up log of a shelf-picking model, shaped like CP-SAT's.
log = ("Starting CP-SAT solver\n\n"
       "Initial optimization model '': (model_fingerprint: 0x51)\n"
       "#Variables: 2'350 (#bools: 2'300 in objective) (2'300 primary variables)\n"
       "  - 2'300 Booleans in [0,1]\n\nStarting presolve at 0.00s\n\n"
       "Presolved optimization model '': (model_fingerprint: 0x52)\n"
       "#Variables: 1'875 (#bools: 1'840 in objective)\n  - 1'840 Booleans in [0,1]\n")
print("variables before and after presolve:", variables_before_and_after(log))
small = log.replace("2'350", "75").replace("1'875", "75")
print("same log with 75 and 75:", variables_before_and_after(small))
