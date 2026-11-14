"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from growth import free_to_grow

m = mathopt.Model()
nurses = m.add_variable(lb=0, ub=25, name="nurses")
grant = m.add_variable(lb=0, name="grant")
overtime = m.add_variable(lb=0, name="overtime")
loan = m.add_variable(lb=-10, ub=float("inf"), name="loan")
m.add_linear_constraint(overtime - nurses <= 30, name="overtime_cap")
m.maximize(4 * nurses + 2 * grant + overtime - loan)

print("free to grow:", free_to_grow(m))
grant.upper_bound = 500
print("with grant capped at 500:", free_to_grow(m))
m.minimize(4 * nurses + 2 * grant + overtime - loan)
print("same terms, minimized:", free_to_grow(m))
