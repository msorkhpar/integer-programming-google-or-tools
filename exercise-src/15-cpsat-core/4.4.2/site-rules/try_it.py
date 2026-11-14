"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.sat.python import cp_model

from site_rules import add_site_rules, site_variables


def check(**fixed):
    model = cp_model.CpModel()
    v = site_variables(model)
    add_site_rules(model, v, 6, 2)
    for name, value in fixed.items():
        model.add(v[name] == value)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    return solver.status_name(solver.solve(model))


print("min_night 6, night with 7 staff:", check(night=1, night_staff=7))
print("min_night 6, night with 3 staff:", check(night=1, night_staff=3))
print("no night, 2 staff:", check(night=0, night_staff=2))
print("freezer shut, 40 frozen orders:", check(freezer=0, frozen_orders=40))
print("forklifts_both 2, both docks, 1 forklift:", check(dock_a=1, dock_b=1, forklifts=1))
print("forklifts_both 2, dock A only, 1 forklift:", check(dock_a=1, dock_b=0, forklifts=1))
