from handout import name_crews


def check(jobs, crews, named):
    """Assert every job has its crews and no crew works two jobs on one day."""
    assert set(named) == set(jobs)
    busy = {}
    for name, (start, days, need) in jobs.items():
        got = list(named[name])
        assert len(got) == need and len(set(got)) == need, f"{name} needs {need} distinct crews, got {got}"
        assert all(c in crews for c in got)
        for c in got:
            for day in range(start, start + days):
                assert (c, day) not in busy, f"crew {c} has {busy[c, day]} and {name} on day {day}"
                busy[c, day] = name


def test_jobs_far_apart_reuse_one_crew():
    jobs = {"a": (0, 2, 1), "b": (3, 2, 1), "c": (7, 1, 1)}
    named = name_crews(jobs, ["X", "Y"])
    check(jobs, ["X", "Y"], named)


def test_every_job_gets_distinct_listed_crews():
    jobs = {"a": (0, 2, 2), "b": (5, 1, 3)}
    named = name_crews(jobs, ["X", "Y", "Z"])
    check(jobs, ["X", "Y", "Z"], named)


def test_jobs_listed_out_of_order_still_fit():
    # Listed late-first: handing out in this order books crews for day 5 before day 0's jobs.
    jobs = {"late": (5, 2, 2), "early": (0, 3, 1), "mid": (2, 3, 1)}
    check(jobs, ["X", "Y"], name_crews(jobs, ["X", "Y"]))


def test_a_crew_is_free_the_day_its_job_ends():
    jobs = {"a": (0, 3, 2), "b": (3, 2, 2), "c": (5, 1, 2)}
    check(jobs, ["X", "Y"], name_crews(jobs, ["X", "Y"]))
