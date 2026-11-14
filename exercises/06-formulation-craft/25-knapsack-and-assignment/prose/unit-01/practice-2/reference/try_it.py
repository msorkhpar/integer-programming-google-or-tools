"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.math_opt.python import mathopt

from lab import Analyzer, build

# id, tests per day, price ($k), floor (m^2), load (kW)
units = [Analyzer("Hema", 400, 180, 9.0, 5.0), Analyzer("Chem", 600, 240, 11.0, 4.0),
         Analyzer("Urin", 250, 100, 5.0, 3.0), Analyzer("Coag", 300, 130, 7.0, 8.0)]


def allowed(plan, budget):
    model, x = build(units, budget, 22.0, 16.0, 12.0, 5.0)
    for aid, var in x.items():
        var.lower_bound = var.upper_bound = 1.0 if aid in plan else 0.0
    return mathopt.solve(model, mathopt.SolverType.HIGHS).termination.reason == mathopt.TerminationReason.OPTIMAL


print("Hema+Chem at budget 420:", allowed({"Hema", "Chem"}, 420))
print("Hema+Chem+Urin at budget 520:", allowed({"Hema", "Chem", "Urin"}, 520))
print("Hema+Chem+Urin at budget 510:", allowed({"Hema", "Chem", "Urin"}, 510))
print("Hema+Chem+Coag at budget 9000:", allowed({"Hema", "Chem", "Coag"}, 9000))
print("Hema+Coag+Urin at budget 9000:", allowed({"Hema", "Coag", "Urin"}, 9000))
