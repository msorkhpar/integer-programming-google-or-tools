"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from tuning import score, tune

configs = ["default", "aggressive", "gentle"]
work = {
    ("east-1", "default"): 3000.0, ("east-1", "aggressive"): 1800.0, ("east-1", "gentle"): 2900.0,
    ("east-2", "default"): 4500.0, ("east-2", "aggressive"): 3000.0, ("east-2", "gentle"): 4200.0,
    ("west-1", "default"): 2500.0, ("west-1", "aggressive"): 2700.0, ("west-1", "gentle"): 2400.0,
    ("west-2", "default"): 5000.0, ("west-2", "aggressive"): 5600.0, ("west-2", "gentle"): 4800.0,
}
train, test = ["east-1", "east-2"], ["west-1", "west-2"]

print("default on train:", round(score(work, "default", train, shift=100), 1))
chosen, on_train, on_test = tune(work, configs, train, test, shift=100)
print("tuned on east, chosen:", chosen)
print("ratio on train:", round(on_train, 3))
print("ratio on test:", round(on_test, 3))
