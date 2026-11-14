"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.sat.python import cp_model

from release import add_rules

features = ["login", "billing", "invoices", "email", "sms", "beta_ui", "classic_ui", "api", "sdk"]
rules = dict(requires=[("billing", "login")], excludes=[("beta_ui", "classic_ui")],
             needs_one_of=[("invoices", ["email", "sms"])], bundles=[("api", "sdk")])


def check(plan):
    model = cp_model.CpModel()
    x = {f: model.new_bool_var(f) for f in features}
    add_rules(model, x, **rules)
    for f, var in x.items():
        model.add(var == (1 if f in plan else 0))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    return solver.status_name(solver.solve(model))


for plan in ({"billing", "login"}, {"billing"}, {"beta_ui", "classic_ui"}, {"invoices"},
             {"invoices", "sms"}, {"api"}, {"api", "sdk"}):
    print("plan", sorted(plan), "->", check(plan))
