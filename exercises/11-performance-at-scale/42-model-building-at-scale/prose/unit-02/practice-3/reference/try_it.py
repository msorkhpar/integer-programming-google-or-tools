"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from compare_models import same_model


def make(order=("a", "b"), coef=0.7, integer=True, maximize=True):
    model = mathopt.Model(name="lots")
    v = {name: model.add_variable(lb=0, ub=1, is_integer=integer, name=name) for name in order}
    model.add_linear_constraint(3.0 * v["a"] + coef * v["b"] <= 4.0, name="space")
    goal = 2.0 * v["a"] + 5.0 * v["b"]
    model.maximize(goal) if maximize else model.minimize(goal)
    return model


print("built b before a:", same_model(make(), make(order=("b", "a"))))
print("coef 0.1 * 7 instead of 0.7:", same_model(make(), make(coef=0.1 * 7)))
print("coef 0.71:", same_model(make(), make(coef=0.71)))
print("continuous variables:", same_model(make(), make(integer=False)))
print("minimize instead:", same_model(make(), make(maximize=False)))
