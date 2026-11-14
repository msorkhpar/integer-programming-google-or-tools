"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from renewal import Job, as_hint, greedy_plan

years = (2031, 2032)
jobs = [Job("birch", 250, 500, years), Job("cedar", 150, 450, years),
        Job("maple", 300, 400, (2031,), must=True), Job("hazel", 100, 120, years)]
budget = {2031: 450, 2032: 300}

plan = greedy_plan(jobs, budget)
print("greedy plan, budgets 450/300:", plan)

model = mathopt.Model()
x = {(j.name, y): model.add_binary_variable(name=f"x_{j.name}_{y}") for j in jobs for y in j.years}
hint = as_hint(x, plan)
print("hint values set to 1:", sorted(v.name for v, value in hint.variable_values.items() if value == 1.0))
print("hint size:", len(hint.variable_values))
