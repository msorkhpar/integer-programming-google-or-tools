"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from verdict import verdict


def show(label, result):
    gap, ok = result
    print(label, round(gap, 6), ok)


show("max 2000 vs bound 2001, tol 1e-3:", verdict(2000.0, 2001.0, 1e-3, "max", False))
show("max 2000 vs bound 2004, tol 1e-3:", verdict(2000.0, 2004.0, 1e-3, "max", False))
show("max 7300 vs bound 7300.8, integral, tol 1e-6:", verdict(7300, 7300.8, 1e-6, "max", True))
show("min 860 vs bound 858.2, integral, tol 1e-3:", verdict(860, 858.2, 1e-3, "min", True))
