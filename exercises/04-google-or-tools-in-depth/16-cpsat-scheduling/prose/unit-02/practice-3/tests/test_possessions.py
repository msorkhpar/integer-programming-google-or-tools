from possessions import possession_plan


def check(jobs, possessions, start):
    """Assert the plan keeps every rule; return the day the last job ends."""
    assert set(start) == set(jobs)
    for name, (line, days) in jobs.items():
        s = start[name]
        assert isinstance(s, int)
        assert any(first <= s and s + days - 1 <= last for first, last in possessions[line]), \
            f"{name} on days {s}-{s + days - 1} is not inside one possession of {line}"
    for a, (la, da) in jobs.items():
        for b, (lb, db) in jobs.items():
            if a < b and la == lb:
                assert start[a] + da <= start[b] or start[b] + db <= start[a], f"{a} and {b} overlap on {la}"
    return max(start[n] + d for n, (_, d) in jobs.items())


def test_jobs_on_different_lines_run_together():
    jobs = {"x": ("north", 2), "y": ("south", 3), "z": ("east", 1)}
    possessions = {"north": [(1, 5)], "south": [(1, 9)], "east": [(1, 1), (6, 8)]}
    assert possession_plan(jobs, possessions) == {"x": 1, "y": 1, "z": 1}


def test_every_job_gets_a_start():
    start = possession_plan({"x": ("north", 2)}, {"north": [(3, 7)]})
    assert set(start) == {"x"} and isinstance(start["x"], int) and 3 <= start["x"] <= 6


def test_a_job_stays_inside_one_possession():
    jobs = {"a1": ("west", 3), "a2": ("west", 3)}
    possessions = {"west": [(0, 4), (10, 20)]}
    # The first possession has 5 days: one job fits, the other waits for day 10.
    assert check(jobs, possessions, possession_plan(jobs, possessions)) == 13


def test_one_job_per_line_at_a_time():
    jobs = {"a": ("west", 2), "b": ("west", 2), "c": ("east", 2)}
    possessions = {"west": [(0, 9)], "east": [(0, 9)]}
    assert check(jobs, possessions, possession_plan(jobs, possessions)) == 4
