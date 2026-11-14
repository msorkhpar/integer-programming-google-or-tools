"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from two_pass import two_pass

cost = [6, 4, 4, 3, 2]
leaks = [15, 11, 9, 6, 5]
hours = [9, 2, 8, 6, 1]

model = mathopt.Model(name="mains")
x = [model.add_binary_variable(name=f"main_{i}") for i in range(len(cost))]
model.add_linear_constraint(sum(c * v for c, v in zip(cost, x)) <= 11, name="budget")
first = mathopt.LinearExpression() + sum(a * v for a, v in zip(leaks, x))
second = mathopt.LinearExpression() + sum(h * v for h, v in zip(hours, x))

for rel in (0.0, 0.1, 0.25):
    print(f"max leaks within {rel:.0%}, then min hours:",
          two_pass(model, first, second, first_max=True, second_max=False, rel_tol=rel))
print("max leaks within 4, then min hours:",
      two_pass(model, first, second, first_max=True, second_max=False, abs_tol=4))
