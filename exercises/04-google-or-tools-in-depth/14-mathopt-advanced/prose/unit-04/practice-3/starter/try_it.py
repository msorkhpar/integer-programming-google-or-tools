"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from without import build, objective_without

HIGHS = mathopt.SolverType.HIGHS
# name -> (value per radio, cost per radio, most radios)
towers = {"quarry": (8, 3, 2), "pier": (6, 2, 2), "chapel": (4, 2, 1), "depot": (5, 4, 1)}
model, u = build(towers, 10)

print("best with every tower:", mathopt.solve(model, HIGHS).objective_value())
print("best without quarry:", objective_without(model, [u["quarry"]], HIGHS))
print("best without pier and chapel:", objective_without(model, [u["pier"], u["chapel"]], HIGHS))
print("upper bounds afterwards:", {k: v.upper_bound for k, v in u.items()})
