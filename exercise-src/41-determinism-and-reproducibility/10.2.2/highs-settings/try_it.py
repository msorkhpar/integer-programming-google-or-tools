"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from highs_settings import highs_parameters

crates = {"C1": (3, 5), "C2": (4, 8), "C3": (2, 3), "C4": (5, 9)}     # weight (t), value

params = highs_parameters(seed=17, threads=2, nodes=200)
print("seed:", params.random_seed)
print("node limit:", params.node_limit)
print("HiGHS threads option:", params.highs.int_options["threads"] if params.highs else None)

model = mathopt.Model()
x = {k: model.add_binary_variable(name=k) for k in crates}
model.add_linear_constraint(sum(w * x[k] for k, (w, _) in crates.items()) <= 8, name="van")
model.maximize(sum(v * x[k] for k, (_, v) in crates.items()))
result = mathopt.solve(model, mathopt.SolverType.HIGHS, params=params)
print("status:", result.termination.reason.name, "value of an 8 t van:", round(result.objective_value()))
