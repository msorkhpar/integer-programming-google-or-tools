"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from poles import build_counted, build_named

cost = {2031: 7, 2032: 8, 2033: 10}
risk = {2031: 2, 2032: 5, 2033: 0}
crew = {2031: 4, 2032: 5, 2033: 6}

for build in (build_named, build_counted):
    model, v = build(9, cost, risk, crew)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    print(f"{build.__name__} for 9 poles: variables", len(v), "cost", round(result.objective_value(), 3))
model, n = build_counted(9, cost, risk, crew)
result = mathopt.solve(model, mathopt.SolverType.HIGHS)
print("counted plan for 9 poles:", {y: round(result.variable_values(v)) for y, v in n.items()})
