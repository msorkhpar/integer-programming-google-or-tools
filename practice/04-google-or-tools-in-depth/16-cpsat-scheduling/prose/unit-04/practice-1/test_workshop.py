from workshop import least_penalty


def penalty_of(jobs, mechanics, horizon, start):
    """Assert the plan keeps every rule; return its total penalty, counted by hand."""
    assert set(start) == set(jobs)
    for name, (days, _, _, _) in jobs.items():
        assert isinstance(start[name], int) and 0 <= start[name] and start[name] + days <= horizon
    for t in range(horizon):
        used = sum(need for name, (days, need, _, _) in jobs.items() if start[name] <= t < start[name] + days)
        assert used <= mechanics, f"day {t} needs {used} mechanics, there are {mechanics}"
    return sum(p * max(0, start[n] + d - due) for n, (d, _, due, p) in jobs.items())


def test_jobs_that_fit_their_due_days_cost_nothing():
    jobs = {"a": (2, 1, 2, 5), "b": (3, 1, 3, 5), "c": (2, 1, 2, 5)}
    total, start = least_penalty(jobs, 3, 20)
    assert penalty_of(jobs, 3, 20, start) == 0


def test_every_job_gets_a_start():
    jobs = {"a": (2, 1, 9, 1)}
    total, start = least_penalty(jobs, 1, 10)
    assert set(start) == {"a"} and isinstance(start["a"], int) and 0 <= start["a"] <= 8


def test_finishing_early_earns_nothing():
    jobs = {"early": (1, 1, 10, 1), "tight": (3, 1, 2, 1), "next": (2, 1, 3, 1)}
    # One mechanic. tight and next cannot both be on time: either order is 3 days late in all.
    # early fits anywhere before day 10; its spare days are not a credit against the 3.
    total, start = least_penalty(jobs, 1, 20)
    assert total == 3
    assert penalty_of(jobs, 1, 20, start) == 3
    jobs = {"a": (2, 1, 2, 5), "b": (3, 1, 3, 5), "c": (2, 1, 4, 5)}
    assert least_penalty(jobs, 2, 20)[0] == 0


def test_the_penalty_decides_who_waits():
    jobs = {"cheap": (2, 2, 2, 1), "dear": (4, 2, 4, 6)}
    # dear first: cheap is 4 days late (4). cheap first: dear is 2 days late (12).
    total, start = least_penalty(jobs, 2, 20)
    assert total == penalty_of(jobs, 2, 20, start) == 4
    assert start["dear"] == 0
