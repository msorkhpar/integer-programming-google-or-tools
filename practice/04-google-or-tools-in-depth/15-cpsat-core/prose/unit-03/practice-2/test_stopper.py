import random

from ortools.sat.python import cp_model

from stopper import TargetStopper


def loading_model() -> cp_model.CpModel:
    """A truck-loading problem of 40 crates, invented for the tests."""
    rng = random.Random(7)
    values = [rng.randint(5, 40) for _ in range(40)]
    weights = [rng.randint(3, 20) for _ in range(40)]
    model = cp_model.CpModel()
    x = [model.new_bool_var(f"crate{i}") for i in range(40)]
    model.add(sum(w * v for w, v in zip(weights, x)) <= 150)
    model.maximize(sum(c * v for c, v in zip(values, x)))
    return model


def solver() -> cp_model.CpSolver:
    """One worker and a plain search, so the run repeats and reports many improving solutions."""
    s = cp_model.CpSolver()
    s.parameters.num_workers = 1
    s.parameters.cp_model_presolve = False
    s.parameters.linearization_level = 0
    return s


class Every(cp_model.CpSolverSolutionCallback):
    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.objectives = []

    def on_solution_callback(self):
        self.objectives.append(self.objective_value)


def full_run() -> list[float]:
    every = Every()
    solver().solve(loading_model(), every)
    return every.objectives


def test_every_solution_is_recorded_in_order():
    stopper = TargetStopper(10_000)                       # out of reach: the search runs to the end
    status = solver().solve(loading_model(), stopper)
    assert status == cp_model.OPTIMAL
    assert stopper.objectives == full_run()


def test_the_search_stops_at_the_first_solution_past_the_target():
    run = full_run()
    target = (run[3] + run[4]) / 2                         # between the 4th and 5th solutions
    stopper = TargetStopper(target)
    status = solver().solve(loading_model(), stopper)
    assert status == cp_model.FEASIBLE
    assert stopper.objectives == run[:5]


def test_a_solution_equal_to_the_target_stops_the_search():
    run = full_run()
    stopper = TargetStopper(run[6])
    solver().solve(loading_model(), stopper)
    assert stopper.objectives == run[:7]
