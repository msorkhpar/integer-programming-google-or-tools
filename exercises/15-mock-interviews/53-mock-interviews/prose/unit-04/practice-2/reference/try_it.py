"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.math_opt.python import mathopt

from elastic import Project, build

projects = [
    Project("B1", 2031, 120, must_do=True),
    Project("B2", 2031, 50, must_do=True),
    Project("B3", 2032, 70, must_do=True),
    Project("B4", 2032, 25),
]

for budgets, penalty in (({2031: 200, 2032: 100}, {2031: 1.0, 2032: 1.0}),
                         ({2031: 150, 2032: 60}, {2031: 1.0, 2032: 1.0}),
                         ({2031: 150, 2032: 60}, {2031: 1.0, 2032: 3.0})):
    model, x = build(projects, budgets, penalty)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    funded = sorted(p for p, v in x.items() if result.variable_values(v) > 0.5)
    print(f"budgets {budgets}, penalty {penalty}:", result.termination.reason.name,
          round(result.objective_value(), 2), funded)
