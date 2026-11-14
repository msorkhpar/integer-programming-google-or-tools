"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from relimit import replace_upper

# A boiler rule: if run_b2 = 1, then 30 <= heat + 0.25 gas <= 150.
model = mathopt.Model(name="heating")
run = model.add_binary_variable(name="run_b2")
heat = model.add_variable(lb=0, ub=300, name="heat_b2")
gas = model.add_variable(lb=0, ub=400, name="gas_b2")
ic = model.add_indicator_constraint(indicator=run, implied_expr=heat + 0.25 * gas, implied_lb=30,
                                    implied_ub=150, name="boiler_b2")

new = replace_upper(model, ic, 110)
print("new upper limit:", new.upper_bound)
print("new lower limit:", new.lower_bound)
print("new name and indicator:", new.name, new.indicator_variable.name, "on zero", new.activate_on_zero)
print("new terms:", {t.variable.name: t.coefficient for t in new.terms()})
print("indicator constraints in the model:", model.get_num_indicator_constraints())
