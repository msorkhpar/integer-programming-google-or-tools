import math
import random

from ortools.sat.python import cp_model

from repeatable import repeatable_solver


def trimming_model():
    """A cooperative's tree-trimming jobs over two crews' hours, not the lesson's portfolio."""
    rng = random.Random(11)
    jobs = [(rng.randint(10, 99), rng.randint(5, 40), rng.randint(5, 40)) for _ in range(40)]
    model = cp_model.CpModel()
    pick = [model.new_bool_var(f"job{i}") for i in range(len(jobs))]
    model.add(sum(h1 * p for (_, h1, _), p in zip(jobs, pick)) <= 300)
    model.add(sum(h2 * p for (_, _, h2), p in zip(jobs, pick)) <= 300)
    model.maximize(sum(v * p for (v, _, _), p in zip(jobs, pick)))
    return model, pick


def run(seed, work):
    model, pick = trimming_model()
    solver = repeatable_solver(seed, work)
    status = solver.solve(model)
    return (solver.status_name(status), solver.objective_value, solver.num_branches, solver.num_conflicts,
            tuple(solver.value(p) for p in pick)), solver


def test_the_solver_runs_one_worker_with_the_given_seed():
    solver = repeatable_solver(42, 2.0)
    assert solver.parameters.num_workers == 1
    assert solver.parameters.random_seed == 42


def test_two_solves_of_one_model_agree_on_every_count():
    first, solver = run(5, 0.5)
    second, _ = run(5, 0.5)
    assert solver.parameters.num_workers == 1
    assert first == second


def test_the_limit_is_work_not_seconds():
    solver = repeatable_solver(1, 3.0)
    assert solver.parameters.max_deterministic_time == 3.0
    assert math.isinf(solver.parameters.max_time_in_seconds)
