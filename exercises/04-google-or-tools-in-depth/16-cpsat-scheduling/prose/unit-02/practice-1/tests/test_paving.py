from paving import paving_plan


def check(jobs, gangs, horizon, start):
    """Assert the plan keeps every rule; return the day the last job ends."""
    assert set(start) == set(jobs)
    for name, (days, _) in jobs.items():
        assert isinstance(start[name], int) and 0 <= start[name] and start[name] + days <= horizon
    for t in range(horizon):
        used = sum(need for name, (days, need) in jobs.items() if start[name] <= t < start[name] + days)
        assert used <= gangs, f"day {t} needs {used} gangs, the pool has {gangs}"
    return max(start[n] + d for n, (d, _) in jobs.items())


def test_one_gang_jobs_share_the_pool():
    jobs = {"a": (3, 1), "b": (3, 1), "c": (2, 1), "d": (2, 1)}
    assert check(jobs, 2, 20, paving_plan(jobs, 2, 20)) == 5


def test_every_job_gets_a_start():
    jobs = {"a": (2, 1), "b": (4, 1)}
    start = paving_plan(jobs, 3, 10)
    assert set(start) == {"a", "b"}
    assert all(isinstance(s, int) and s >= 0 for s in start.values())


def test_a_job_holds_all_the_gangs_it_needs():
    jobs = {"wide": (4, 2), "a": (4, 1), "b": (4, 1)}
    # With 2 gangs, "wide" runs alone, and a and b run together: 8 days.
    assert check(jobs, 2, 20, paving_plan(jobs, 2, 20)) == 8


def test_a_job_bigger_than_the_pool_gives_no_plan():
    assert paving_plan({"huge": (2, 4), "a": (1, 1)}, 3, 10) == {}
