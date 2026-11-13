"""HiGHS's own suggestion for the mixed-unit model: scale the objective by a power of two."""

from ortools.math_opt.python import mathopt
from ortools.math_opt.solvers import highs_pb2

from gridcap import generate
from loan_model import MIXED, build, solve

lm = build(generate("small"), MIXED)
params = mathopt.SolveParameters(highs=highs_pb2.HighsOptionsProto(int_options={"user_objective_scale": -3}))
result, log = solve(lm.model, params=params)
for line in log[:8]:
    print(line)
print("...")
print(log[-1])
print(f"result.objective_value(): {result.objective_value():,.1f}")
