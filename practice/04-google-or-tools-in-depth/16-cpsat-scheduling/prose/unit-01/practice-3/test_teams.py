from teams import split_work


def check(jobs, teams, away, horizon, plan):
    """Assert the plan keeps every rule; return the day the last job ends."""
    assert set(plan) == set(jobs)
    days_of = {t: {} for t in teams}
    for j, (team, s) in plan.items():
        assert team in teams, f"{j} goes to {team!r}, not a listed team"
        assert isinstance(s, int) and 0 <= s and s + jobs[j] <= horizon
        for day in range(s, s + jobs[j]):
            assert day not in days_of[team], f"{team} has {j} and {days_of[team][day]} on day {day}"
            days_of[team][day] = j
    for t, spans in away.items():
        for first, last in spans:
            for day in range(first, last + 1):
                assert day not in days_of[t], f"{t} is away on day {day} but does {days_of[t][day]}"
    return max(s + jobs[j] for j, (_, s) in plan.items())


def test_every_job_goes_to_a_listed_team():
    jobs = {"tank": 2, "weir": 1}
    plan = split_work(jobs, ["red"], {}, 10)
    assert {team for team, _ in plan.values()} == {"red"}
    assert all(isinstance(s, int) and s >= 0 for _, s in plan.values())


def test_one_team_does_everything_in_turn():
    jobs = {"tank": 2, "weir": 1, "pump": 3}
    assert check(jobs, ["red"], {}, 10, split_work(jobs, ["red"], {}, 10)) == 6


def test_two_teams_work_at_the_same_time():
    jobs = {"tank": 3, "weir": 3, "pump": 2, "main": 2}
    assert check(jobs, ["red", "blue"], {}, 20, split_work(jobs, ["red", "blue"], {}, 20)) == 5


def test_a_team_away_does_not_stop_the_other():
    jobs = {"tank": 3, "weir": 2}
    away = {"blue": [(0, 1)]}
    # red starts the tank on day 0; blue is back on day 2 and does the weir: the work ends on day 4.
    assert check(jobs, ["red", "blue"], away, 20, split_work(jobs, ["red", "blue"], away, 20)) == 4
