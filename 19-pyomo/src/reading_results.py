"""Lesson 5.1.2: solve the Pyomo timing model with HiGHS and read what came back.

GridCap is a fictional utility's portfolio. Four solves of the same model: proven optimal, optimal
within HiGHS's default gap, infeasible, and stopped by a node limit. Each prints the fields of
Pyomo's results object that tell those cases apart.
"""

import pyomo.environ as pyo
from pyomo.contrib.solver.common.factory import SolverFactory

from gridcap import generate
from pyomo_timing import build

small = generate("small")
opt = SolverFactory("highs")          # Pyomo's newer solver interface to HiGHS (highspy)


def report(label, results):
    print(f"{label:16} {results.termination_condition.name:31} {results.solution_status.name:10}"
          f" incumbent {results.incumbent_objective}  bound {results.objective_bound}")


# 1. Asked for a proven optimum: incumbent and bound meet.
m = build(small)
results = opt.solve(m, rel_gap=0.0)
report("rel_gap=0", results)
print("  loaded into the model: x[P031,2028] =", m.x["P031", 2028].value, " objective", pyo.value(m.value))

# 2. HiGHS's own default gap: "optimal" means within that gap of the bound.
results = opt.solve(build(small))
report("default gap", results)
gap = (results.objective_bound - results.incumbent_objective) / results.incumbent_objective
print(f"  relative gap {gap:.2e}")

# 3. Infeasible: by default the solve raises; ask it to return instead, and load nothing.
broke = build(small)
for y in broke.Y:
    broke.budget[y] = 0
try:
    opt.solve(broke)
except Exception as error:
    print("infeasible        raises", type(error).__name__)
results = opt.solve(broke, raise_exception_on_nonoptimal_result=False, load_solutions=False)
report("  returned", results)

# 3b. load_solutions=False on a model that has a plan: nothing is on the variables until load_vars().
kept = build(small)
results = opt.solve(kept, rel_gap=0.0, raise_exception_on_nonoptimal_result=False, load_solutions=False)
report("not loaded", results)
print("  before load_vars: x[P031,2028] =", kept.x["P031", 2028].value)
results.solution_loader.load_vars()
print("  after load_vars:  x[P031,2028] =", kept.x["P031", 2028].value, " objective", pyo.value(kept.value))

# 4. A limit stops the search: a feasible plan is loaded, but it is not proven optimal.
medium = build(generate("medium"))
results = opt.solve(medium, solver_options={"mip_max_nodes": 1}, raise_exception_on_nonoptimal_result=False)
report("medium, 1 node", results)
print("  plan loaded:", sum(1 for v in medium.x.values() if v.value > 0.5), "starts; objective", pyo.value(medium.value))

# 5. The older interface most existing Pyomo code uses: pyo.SolverFactory and a SolverResults object.
legacy = pyo.SolverFactory("appsi_highs")
legacy.config.mip_gap = 0.0
old = legacy.solve(build(small))
print("legacy           ", old.solver.status, old.solver.termination_condition,
      " lower", old.problem.lower_bound, " upper", old.problem.upper_bound)
print("  check_optimal_termination:", pyo.check_optimal_termination(old))

# 6. A forgotten bound: a new integer "loan" variable with no upper bound and a positive objective.
loose = build(small)
loose.loan = pyo.Var(domain=pyo.NonNegativeIntegers)
loose.value.expr = loose.value.expr + loose.loan
results = opt.solve(loose, raise_exception_on_nonoptimal_result=False, load_solutions=False)
report("unbounded MILP", results)
