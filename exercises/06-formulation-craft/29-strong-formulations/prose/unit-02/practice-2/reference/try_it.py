"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from programme import Talk, build, clashes

talks = [Talk("Graphs", "rui", 5, 6), Talk("Cuts", "sam", 4, 5),
         Talk("Heuristics", "rui", 2, 3), Talk("Pricing", "tia", 3, 4)]
LAB = 8

print("clashing pairs at lab 8:", sorted(sorted(p) for p in clashes(talks, LAB)))
for integer in (True, False):
    model, x = build(talks, LAB, integer=integer)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    print(f"integer={integer} rows:", sum(1 for _ in model.linear_constraints()))
    print(f"integer={integer} value:", round(result.objective_value(), 3),
          {n: round(result.variable_values(v), 2) for n, v in x.items()})
