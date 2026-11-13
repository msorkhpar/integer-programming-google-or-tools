from ortools.sat.python import cp_model

from audit import record


def feeder_model(names):
    """A utility's feeder upgrades under a budget, not the lesson's portfolio."""
    costs = {"F1": 40, "F2": 35, "F3": 25, "F4": 30, "F5": 20}
    gains = {"F1": 60, "F2": 50, "F3": 30, "F4": 45, "F5": 25}
    model = cp_model.CpModel()
    pick = {n: model.new_bool_var(n) for n in names}
    model.add(sum(costs[n] * pick[n] for n in names) <= 100)
    model.maximize(sum(gains[n] * pick[n] for n in names))
    return model, pick


def solve(names):
    model, pick = feeder_model(names)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    solver.parameters.random_seed = 3
    status = solver.solve(model)
    return record(solver, status, pick)


def test_two_repeatable_runs_give_equal_records():
    names = ["F1", "F2", "F3", "F4", "F5"]
    assert solve(names) == solve(names)
    assert solve(names) != ()


def test_the_record_holds_status_objective_and_chosen_names():
    assert solve(["F1", "F2", "F3", "F4", "F5"]) == ("OPTIMAL", 140, ("F1", "F2", "F3"))


def test_the_record_does_not_depend_on_the_order_variables_were_made():
    assert solve(["F5", "F4", "F3", "F2", "F1"]) == ("OPTIMAL", 140, ("F1", "F2", "F3"))
