"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from direction import price_directions

depots = {"west": (35, 50), "quay": (20, 26)}


def solved(budget, cap):
    m = mathopt.Model()
    x = {s: m.add_binary_variable(name=s) for s in depots}
    overtime = m.add_variable(lb=0, ub=cap, name="overtime")
    m.add_linear_constraint(sum(c * x[s] for s, (c, _) in depots.items()) + overtime <= budget, name="budget")
    m.maximize(sum(v * x[s] for s, (_, v) in depots.items()) + 0.25 * overtime)
    return m, mathopt.solve(m, mathopt.SolverType.HIGHS)


m, result = solved(budget=60, cap=10)
print("budget 60, overtime cap 10, step 3:", price_directions(m, result, "budget", 3))
m, result = solved(budget=60, cap=5)
print("budget 60, overtime cap 5, step 3:", price_directions(m, result, "budget", 3))
