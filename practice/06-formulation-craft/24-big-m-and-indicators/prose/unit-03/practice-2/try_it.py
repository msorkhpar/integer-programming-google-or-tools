"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from ortools.sat.python import cp_model

from crew_hours import add_hours_rules, crew_variables


def allowed(worked, approved):
    model = cp_model.CpModel()
    hours, overtime = crew_variables(model)
    add_hours_rules(model, hours, overtime)
    model.add(hours == worked)
    model.add(overtime == int(approved))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    return solver.solve(model) in (cp_model.OPTIMAL, cp_model.FEASIBLE)


for worked, approved in [(36, False), (41, False), (48, True), (43, True), (57, True)]:
    print(f"{worked} hours, overtime {approved}:", allowed(worked, approved))
