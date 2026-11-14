"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from explain import explain

B = mathopt.ModelSubsetBounds

# A barge plan: tonnes must reach 90, the quay takes at most 70.
model = mathopt.Model(name="barge")
tonnes = model.add_integer_variable(lb=0, ub=80, name="tonnes")
quay = model.add_linear_constraint(tonnes <= 70, name="quay")
order = model.add_linear_constraint(tonnes >= 90, name="order")
subset = mathopt.ModelSubset(linear_constraints={order: B(lower=True), quay: B(upper=True)},
                             variable_bounds={tonnes: B(upper=True)},
                             variable_integrality=frozenset({tonnes}))

for status in (mathopt.FeasibilityStatus.INFEASIBLE, mathopt.FeasibilityStatus.FEASIBLE):
    found = mathopt.ComputeInfeasibleSubsystemResult(feasibility=status, infeasible_subsystem=subset, is_minimal=False)
    print(f"lines when {status.name}:", explain(found))
