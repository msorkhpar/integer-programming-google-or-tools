"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.math_opt.python import mathopt

from repairs import Repair, build

repairs = [
    Repair("G1", 35, 28, 8),
    Repair("G2", 25, 15, 14, main="Elm St"),
    Repair("G3", 45, 22, 25, main="Elm St"),
    Repair("G4", 30, 18, 6),
]

for budget, floor in ((90, 0), (90, 30), (110, 35), (60, 40)):
    model, x = build(repairs, budget, floor)
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    if result.termination.reason == mathopt.TerminationReason.OPTIMAL:
        funded = sorted(r for r, v in x.items() if result.variable_values(v) > 0.5)
        print(f"budget {budget}, risk floor {floor}: NPV {round(result.objective_value())}, funded {funded}")
    else:
        print(f"budget {budget}, risk floor {floor}:", result.termination.reason.name)
