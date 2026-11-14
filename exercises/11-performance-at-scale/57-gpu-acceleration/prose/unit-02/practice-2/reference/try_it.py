"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from runs import check_runs


def run(device, solver, objective, digest):
    return {"device": device, "solver": solver, "objective": objective, "digest": digest}


agree = [run("cpu", "simplex", 250.0, "aa11"), run("cpu", "ipm", 250.0000001, "bb22"),
         run("gpu", "pdlp", 250.00002, "cc33"), run("gpu", "pdlp", 250.00002, "cc33")]
print("four runs near 250, tol 1e-6:", check_runs(agree, 1e-6))
print("same runs, tol 1e-8:", check_runs(agree, 1e-8))
print("a pdlp repeat with another digest:", check_runs(agree + [run("gpu", "pdlp", 250.00002, "dd44")], 1e-6))
print("gpu runs only:", check_runs(agree[2:], 1e-6))
