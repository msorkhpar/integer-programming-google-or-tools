"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from stopper import stop_at


def ask(target, primal, dual):
    data = mathopt.CallbackData(event=mathopt.Event.MIP_SOLUTION,
                                mip_stats=mathopt.MipStats(primal_bound=primal, dual_bound=dual))
    return stop_at(target)(data).terminate


print("target 0.01, primal 500, dual 504:", ask(0.01, 500.0, 504.0))
print("target 0.01, primal 500, dual 510:", ask(0.01, 500.0, 510.0))
print("target 0.05, primal 800, dual 770:", ask(0.05, 800.0, 770.0))
print("target 0.05, primal 0, dual 3:", ask(0.05, 0.0, 3.0))
print("target 0.05, primal -inf, dual 900:", ask(0.05, float("-inf"), 900.0))
