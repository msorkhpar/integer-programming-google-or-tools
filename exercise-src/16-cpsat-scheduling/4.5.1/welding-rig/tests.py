from rig import shortest_schedule


def busy_days(jobs, start):
    """Day -> the jobs at work on it."""
    days = {}
    for name, d in jobs.items():
        for day in range(start[name], start[name] + d):
            days.setdefault(day, []).append(name)
    return days


def check(jobs, booked, horizon, start):
    assert set(start) == set(jobs)
    for name, d in jobs.items():
        assert isinstance(start[name], int)
        assert 0 <= start[name] and start[name] + d <= horizon
    days = busy_days(jobs, start)
    assert all(len(names) == 1 for names in days.values()), f"two jobs on one day: {days}"
    for first, last in booked:
        for day in range(first, last + 1):
            assert day not in days, f"day {day} is booked but {days[day]} runs on it"
    return max(start[n] + d for n, d in jobs.items())


def test_every_job_gets_a_start():
    jobs = {"north": 2, "south": 5}
    start = shortest_schedule(jobs, [], 10)
    assert set(start) == {"north", "south"}
    assert all(isinstance(s, int) and s >= 0 for s in start.values())
    assert start["north"] + 2 <= 10 and start["south"] + 5 <= 10


def test_jobs_never_overlap_and_finish_early():
    jobs = {"a": 3, "b": 2, "c": 4}
    assert check(jobs, [], 20, shortest_schedule(jobs, [], 20)) == 9


def test_booked_days_stay_free():
    jobs = {"a": 3, "b": 3, "c": 2}
    booked = [(2, 3), (7, 9)]
    # 0-1 fits c; 4-6 fits a or b; the other one goes after day 9: ends at 13.
    assert check(jobs, booked, 30, shortest_schedule(jobs, booked, 30)) == 13


def test_a_one_day_booking_blocks_its_day():
    jobs = {"a": 4, "b": 4}
    booked = [(4, 4)]
    assert check(jobs, booked, 20, shortest_schedule(jobs, booked, 20)) == 9
