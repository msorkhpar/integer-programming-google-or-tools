from ortools.sat.python import cp_model

from crew import Job, build

# A substation inspection crew, not the lessons' vegetation crews.
JOBS = [Job("A", 3, 0, 10), Job("B", 2, 2, 12), Job("C", 4, 0, 20)]
BLOCKED = [(6, 7)]          # the crew is away in weeks 6 and 7
HORIZON = 20


def allowed(starts: dict[str, int]) -> bool:
    """Fix each job's start week and ask CP-SAT whether the model accepts the schedule."""
    model, start = build(JOBS, BLOCKED, HORIZON)
    for name, week in starts.items():
        model.add(start[name] == week)
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = 1
    return solver.solve(model) in (cp_model.OPTIMAL, cp_model.FEASIBLE)


def test_two_jobs_at_once_are_refused():
    assert allowed({"A": 0, "B": 9, "C": 14}) is True
    assert allowed({"A": 0, "B": 2, "C": 8}) is False


def test_no_work_in_a_blocked_period():
    assert allowed({"A": 0, "B": 9, "C": 14}) is True
    assert allowed({"A": 0, "B": 3, "C": 5}) is False


def test_a_job_that_ends_after_its_deadline_is_refused():
    assert allowed({"A": 0, "B": 9, "C": 14}) is True
    assert allowed({"A": 11, "B": 3, "C": 15}) is False


def test_jobs_may_run_back_to_back():
    assert allowed({"A": 0, "B": 3, "C": 8}) is True
    assert allowed({"A": 0, "B": 2, "C": 8}) is False


def test_a_job_may_end_exactly_at_its_deadline():
    assert allowed({"A": 0, "B": 10, "C": 12}) is True
    assert allowed({"A": 11, "B": 3, "C": 15}) is False


def test_the_deadline_is_on_the_end_not_the_start():
    assert allowed({"A": 0, "B": 9, "C": 14}) is True
    assert allowed({"A": 0, "B": 11, "C": 14}) is False


def test_the_last_week_of_a_blocked_period_is_blocked_too():
    assert allowed({"A": 0, "B": 8, "C": 12}) is True
    assert allowed({"A": 0, "B": 7, "C": 12}) is False
