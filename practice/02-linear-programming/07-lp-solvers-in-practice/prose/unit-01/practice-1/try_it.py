"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

import random

from ortools.math_opt.python import mathopt

from methods import Algo, run_method

# A random 30-variable, 15-row packing LP.
rng = random.Random(11)
model = mathopt.Model(name="crates")
x = [model.add_variable(lb=0, ub=rng.randint(2, 8), name=f"x{j}") for j in range(30)]
for i in range(15):
    model.add_linear_constraint(sum(rng.randint(1, 9) * x[j] for j in rng.sample(range(30), 10)) <= rng.randint(30, 80))
model.maximize(sum(rng.randint(1, 15) * v for v in x))

for solver, algorithm in ((mathopt.SolverType.GLOP, Algo.PRIMAL_SIMPLEX), (mathopt.SolverType.HIGHS, Algo.BARRIER),
                          (mathopt.SolverType.PDLP, Algo.FIRST_ORDER), (mathopt.SolverType.GLOP, Algo.BARRIER)):
    print(f"{solver.name} {algorithm.name}:", run_method(model, solver, algorithm))
