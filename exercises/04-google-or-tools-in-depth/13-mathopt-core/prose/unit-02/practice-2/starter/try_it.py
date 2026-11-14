"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from prices import binding_prices

# A bakery's week: trays of bread and cake under oven hours and flour.
model = mathopt.Model(name="bakery")
bread = model.add_variable(lb=0, ub=40, name="bread")
cake = model.add_variable(lb=0, ub=40, name="cake")
rows = [
    model.add_linear_constraint(2 * bread + 3 * cake <= 60, name="oven"),
    model.add_linear_constraint(bread + cake <= 25, name="flour"),
    model.add_linear_constraint(cake <= 30, name="boxes"),
]
model.maximize(5 * bread + 6 * cake)

prices = binding_prices(mathopt.solve(model, mathopt.SolverType.GLOP), rows)
print("prices from GLOP:", None if prices is None else {k: round(v, 6) for k, v in prices.items()})
bread.integer = True
print("prices from HiGHS with whole trays:", binding_prices(mathopt.solve(model, mathopt.SolverType.HIGHS), rows))
