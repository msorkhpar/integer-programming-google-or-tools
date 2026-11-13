from roster_settings import read_settings

GOOD = {"ROSTER_BUCKET": "roster-example", "SEASON": "2031", "CREWS": "12", "DRY_RUN": "true"}


def test_a_complete_environment_gives_its_settings():
    assert read_settings(GOOD) == (
        {"bucket": "roster-example", "season": 2031, "crews": 12, "dry_run": True}, [])


def test_defaults_fill_crews_and_dry_run():
    assert read_settings({"ROSTER_BUCKET": "roster-example", "SEASON": "2027"}) == (
        {"bucket": "roster-example", "season": 2027, "crews": 4, "dry_run": False}, [])


def test_every_problem_is_reported_at_once():
    settings, problems = read_settings({"SEASON": "next", "CREWS": "0", "DRY_RUN": "maybe"})
    assert settings is None
    assert set(problems) == {"ROSTER_BUCKET is not set", "SEASON='next' is not a whole number",
                             "CREWS 0 is outside 1-50", "DRY_RUN='maybe' is not true or false"}


def test_season_must_be_in_range():
    assert read_settings({**GOOD, "SEASON": "2050"}) == (None, ["SEASON 2050 is outside 2025-2040"])
    assert read_settings({**GOOD, "SEASON": "2025"}) == (
        {"bucket": "roster-example", "season": 2025, "crews": 12, "dry_run": True}, [])


def test_dry_run_reads_true_and_false_in_any_case():
    assert (read_settings({**GOOD, "DRY_RUN": "TRUE"})[0] or {}).get("dry_run") is True
    assert (read_settings({**GOOD, "DRY_RUN": "False"})[0] or {}).get("dry_run") is False


def test_credentials_in_the_environment_are_refused():
    settings, problems = read_settings({**GOOD, "AWS_SECRET_ACCESS_KEY": "x", "DB_PASSWORD": "y"})
    assert settings is None
    assert set(problems) == {"AWS_SECRET_ACCESS_KEY must not be set: use the job role",
                             "DB_PASSWORD must not be set: use the job role"}


def test_a_number_with_a_fraction_is_not_a_whole_number():
    assert read_settings({**GOOD, "CREWS": "4.5"}) == (None, ["CREWS='4.5' is not a whole number"])
