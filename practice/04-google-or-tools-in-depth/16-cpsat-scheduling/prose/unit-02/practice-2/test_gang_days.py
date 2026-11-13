from gang_days import holiday_plan


def check(jobs, available, start):
    """Assert the plan keeps every rule; return the day the last job ends."""
    assert set(start) == set(jobs)
    for name, (days, _) in jobs.items():
        assert isinstance(start[name], int) and 0 <= start[name] and start[name] + days <= len(available)
    for t, gangs in enumerate(available):
        used = sum(need for name, (days, need) in jobs.items() if start[name] <= t < start[name] + days)
        assert used <= gangs, f"day {t} needs {used} gangs, {gangs} are available"
    return max(start[n] + d for n, (d, _) in jobs.items())


def test_a_steady_pool_works_as_before():
    jobs = {"a": (3, 1), "b": (3, 1), "c": (2, 2)}
    available = [2] * 12
    assert check(jobs, available, holiday_plan(jobs, available)) == 5


def test_every_job_gets_a_start():
    jobs = {"a": (2, 1)}
    start = holiday_plan(jobs, [1] * 6)
    assert set(start) == {"a"} and isinstance(start["a"], int) and 0 <= start["a"] <= 4


def test_the_full_pool_is_used_outside_the_dip():
    jobs = {"a": (2, 2), "b": (2, 2), "c": (2, 2)}
    available = [4, 4, 2, 2, 4, 4, 4, 4, 4, 4]
    # Days 0-1 take two jobs at once, days 2-3 one more: the work ends on day 4.
    assert check(jobs, available, holiday_plan(jobs, available)) == 4


def test_a_dip_of_several_days_holds_for_all_of_them():
    jobs = {"a": (2, 2), "b": (2, 2), "c": (2, 2)}
    available = [4, 4, 0, 0, 0, 0, 4, 4, 4, 4]
    # Two jobs on days 0-1, nothing on days 2-5, the third job on days 6-7.
    assert check(jobs, available, holiday_plan(jobs, available)) == 8
