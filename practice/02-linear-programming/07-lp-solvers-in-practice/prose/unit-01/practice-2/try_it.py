"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from renewal import District, all_agree, relative_gap, solve_on

towns = [District("Ashby", 8, 5, 2, 9), District("Brook", 6, 2, 3, 10), District("Cleve", 4, 1, 1, 15)]

values = {s.name: solve_on(towns, 50, 35, s)
          for s in (mathopt.SolverType.GLOP, mathopt.SolverType.HIGHS, mathopt.SolverType.PDLP)}
for name, value in values.items():
    print(f"{name} at budget 50, hours 35:", value if value is None else round(value, 6))
print("all agree within 1e-4:", all_agree(values, 1e-4))
print("gap between 500.0 and 500.2:", round(relative_gap(500.0, 500.2), 6))
