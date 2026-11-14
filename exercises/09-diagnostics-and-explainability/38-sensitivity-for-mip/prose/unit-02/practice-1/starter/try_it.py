"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from rows import row_report

m = mathopt.Model()
lime = m.add_variable(lb=0, name="lime")
alum = m.add_variable(lb=0, name="alum")
m.add_linear_constraint(lime + alum <= 30, name="tank")
m.add_linear_constraint(2 * lime + alum <= 100, name="pump_hours")
m.maximize(4 * lime + 1 * alum)
report = row_report(m, mathopt.solve(m, mathopt.SolverType.GLOP))
for name, row in report.items():
    print(f"row {name}:", {k: round(v, 3) if isinstance(v, float) else v for k, v in row.items()})
