"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.math_opt.python import mathopt

from audit import audit

# A reservoir: a gate (yes/no), the release and the head.
model = mathopt.Model(name="reservoir")
gate = model.add_binary_variable(name="gate")
release = model.add_variable(lb=0, ub=400, name="release")
head = model.add_variable(lb=0, ub=30, name="head")
model.add_indicator_constraint(indicator=gate, activate_on_zero=True, implied_constraint=release <= 0, name="shut")
model.add_indicator_constraint(indicator=gate, implied_constraint=release + 4 * head <= 250, name="spill")
model.add_indicator_constraint(indicator=gate, implied_expr=head, implied_lb=6, implied_ub=18, name="head_band")

rows = audit(model)
print("indicators listed:", len(rows))
for row in rows:
    print("indicator:", row)
