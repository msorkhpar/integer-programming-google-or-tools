"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.math_opt.python import mathopt

from bonus import build

# Jobs at two substations: cost and value; bonus per substation.
cost = {"W1": 3, "W2": 2, "W3": 4, "S1": 5}
value = {"W1": 1, "W2": 2, "W3": 1, "S1": 2}
jobs = {"West": ["W1", "W2", "W3"], "South": ["S1"]}
bonus = {"West": 8, "South": 5}

for budget in (9, 12):
    lp, _, _ = build(cost, value, budget, bonus, jobs, integer=False)
    milp, _, _ = build(cost, value, budget, bonus, jobs)
    print(f"LP bound at budget {budget}:", round(mathopt.solve(lp, mathopt.SolverType.GLOP).objective_value(), 3))
    print(f"best plan at budget {budget}:", round(mathopt.solve(milp, mathopt.SolverType.HIGHS).objective_value(), 3))
