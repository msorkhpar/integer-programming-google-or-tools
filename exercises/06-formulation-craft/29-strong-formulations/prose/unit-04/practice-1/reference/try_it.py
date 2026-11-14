"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from depots import Depots, add_inherited_rules, add_rules, build

d = Depots({"North": 5, "South": 4, "West": 3}, {"Mill": 9, "Quay": 10},
           {"Mill": 20, "Quay": 24},
           {("North", "Mill"): 2, ("North", "Quay"): 5, ("South", "Mill"): 4,
            ("South", "Quay"): 1, ("West", "Mill"): 3, ("West", "Quay"): 3})

for rules in (add_inherited_rules, add_rules):
    for integer in (True, False):
        model, _, y = build(d, rules, integer=integer)
        result = mathopt.solve(model, mathopt.SolverType.HIGHS)
        print(f"{rules.__name__} integer={integer}: cost", round(result.objective_value(), 3),
              {j: round(result.variable_values(v), 3) for j, v in y.items()})
