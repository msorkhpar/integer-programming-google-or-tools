import math

from ortools.sat.python import cp_model

from roster_solver import configure


def roster_model() -> tuple[cp_model.CpModel, dict]:
    """Three crews, six circuits; each circuit trimmed by one crew; a crew trims at most two."""
    model = cp_model.CpModel()
    x = {(c, k): model.new_bool_var(f"x_{c}_{k}") for c in range(6) for k in range(3)}
    for c in range(6):
        model.add_exactly_one(x[c, k] for k in range(3))
    for k in range(3):
        model.add(sum(x[c, k] for c in range(6)) <= 2)
    model.maximize(sum((c + 1) * (k + 1) % 5 * x[c, k] for c in range(6) for k in range(3)))
    return model, x


def test_one_worker_gets_the_seed_and_the_work_limit():
    solver = configure(cp_model.CpSolver(), seed=11, workers=1, work=5.0)
    assert solver.parameters.random_seed == 11
    assert solver.parameters.max_deterministic_time == 5.0
    model, _ = roster_model()
    assert solver.solve(model) == cp_model.OPTIMAL


def test_the_worker_count_uses_the_current_parameter():
    solver = configure(cp_model.CpSolver(), seed=11, workers=4, work=5.0)
    assert solver.parameters.num_workers == 4
    assert solver.parameters.num_search_workers == 0


def test_several_workers_are_interleaved():
    solver = configure(cp_model.CpSolver(), seed=11, workers=4, work=5.0)
    assert solver.parameters.interleave_search is True
    assert solver.parameters.max_deterministic_time == 5.0


def test_the_clock_never_stops_the_search():
    solver = configure(cp_model.CpSolver(), seed=2, workers=1, work=3.0)
    assert math.isinf(solver.parameters.max_time_in_seconds)
    assert solver.parameters.max_deterministic_time == 3.0
