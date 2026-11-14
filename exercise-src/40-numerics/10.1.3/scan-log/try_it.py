"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from scan import scan

log = [
    "MIP roster has 120 rows; 300 cols; 900 nonzeros; 280 integer variables (280 binary)",
    "Coefficient ranges:",
    "  Matrix  [5e-03, 2e+07]",
    "  Cost    [1e+00, 5e+04]",
    "WARNING: Problem has some excessively large costs",
    "  Solution status   feasible",
    "                    2.5e-06 (row viol.)",
    "                    0 (bound viol.)",
]
print("findings, roster log:", scan(log))
print("findings, roster log, span limit 1e10:", scan(log, max_span=1e10))
print("findings, matrix line alone:", scan(["  Matrix  [1e+00, 4e+02]"]))
