from season import best_season


def test_whole_months_pick_the_most_valuable_jobs_that_fit():
    assert best_season([5, 6, 4, 3], [3, 4, 5, 2], 9) == (14, [0, 1, 3])      # 3 + 4 + 2 = 9 months


def test_hundredths_of_a_month_count():
    assert best_season([5, 6], [2.3, 7.71], 10.0) == (6, [1])                 # 2.3 + 7.71 = 10.01 does not fit


def test_a_season_with_a_fraction_keeps_it():
    assert best_season([5, 6], [4.5, 5.0], 9.5) == (11, [0, 1])               # 4.5 + 5.0 fits 9.5 exactly


def test_a_job_longer_than_the_season_is_never_chosen():
    assert best_season([50, 6], [12.5, 3.0], 12.0) == (6, [1])
