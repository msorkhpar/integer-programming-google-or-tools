"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from audit import audit

clashes = [{"bridge_shut_wk3", "paint_wk3"}]


def infeasible(on):
    return any(c <= set(on) for c in clashes)


print("claim bridge+paint:", audit(["bridge_shut_wk3", "paint_wk3"], infeasible))
print("claim bridge+paint+day_shift:", audit(["bridge_shut_wk3", "paint_wk3", "day_shift"], infeasible))
print("claim paint+day_shift:", audit(["paint_wk3", "day_shift"], infeasible))
