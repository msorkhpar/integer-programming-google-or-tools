"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

from ortools.sat.python import cp_model

from roster_outcome import outcome

# Three crews, up to 4 weeks each; maximize 6 per week worked; `weeks` weeks needed in total.
for weeks in (9, 13):
    model = cp_model.CpModel()
    crews = [model.new_int_var(0, 4, f"crew{k}") for k in range(3)]
    model.add(sum(crews) == weeks)
    model.maximize(6 * sum(crews))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    status = solver.solve(model)
    print(f"{weeks} weeks needed:", outcome(status, solver.objective_value, solver.best_objective_bound, 5))

print("FEASIBLE at 45 of bound 60:", outcome(cp_model.FEASIBLE, 45.0, 60.0, 20))
print("UNKNOWN:", outcome(cp_model.UNKNOWN, 0.0, 60.0, 20))
print("MODEL_INVALID:", outcome(cp_model.MODEL_INVALID, 0.0, 0.0, 20)["status"])
