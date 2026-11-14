"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from renewals import coefficients, objective

reference = {"breaks": 5.0, "leakage": 100.0, "npv": 800.0}
weights = {"breaks": 0.5, "leakage": 0.1, "npv": 0.4}
benefits = {("Pine", 2031): {"breaks": 5.0, "leakage": 20.0, "npv": 200.0},
            ("Birch", 2032): {"breaks": 1.0, "leakage": 100.0, "npv": 400.0}}

c = coefficients(benefits, reference, weights)
print("coefficients:", {k: round(v, 2) for k, v in c.items()})
model = mathopt.Model()
x = {key: model.add_binary_variable(name=f"x_{key[0]}_{key[1]}") for key in c}
for plan in ({("Pine", 2031)}, set(c)):
    values = {var: 1.0 if key in plan else 0.0 for key, var in x.items()}
    print(f"plan {sorted(plan)}:", round(mathopt.evaluate_expression(objective(x, c), values), 2))
