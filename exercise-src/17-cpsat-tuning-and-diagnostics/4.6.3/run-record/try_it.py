"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.sat.python import cp_model

from audit import record

# Four pole upgrades, (cost, gain), and a budget.
upgrades = {"P4": (30, 40), "P2": (25, 38), "P3": (20, 22), "P1": (35, 50)}
def run(budget):
    model = cp_model.CpModel()
    pick = {n: model.new_bool_var(n) for n in upgrades}
    model.add(sum(c * pick[n] for n, (c, _) in upgrades.items()) <= budget)
    model.maximize(sum(g * pick[n] for n, (_, g) in upgrades.items()))
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.random_seed = 4
    return record(solver, solver.solve(model), pick)


print("record at budget 70:", run(70))
print("record at budget 70, run again:", run(70))
print("record at budget 45:", run(45))
