"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.sat.python import cp_model

from tier import add_tier_flag


def check(spend, gold, threshold=250):
    model = cp_model.CpModel()
    s = model.new_int_var(0, 600, "spend")
    g = model.new_bool_var("gold")
    add_tier_flag(model, s, g, threshold)
    model.add(s == spend)
    model.add(g == int(gold))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    return solver.status_name(solver.solve(model))


for spend, gold in ((400, True), (400, False), (120, False), (120, True), (250, True), (249, True)):
    print(f"threshold 250, spend {spend}, gold {gold}:", check(spend, gold))
