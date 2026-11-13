from wildfire import go_until

PLANS = [(100, 900), (140, 880), (150, 850), (200, 800), (210, 700), (260, 600)]
# Supported: (100, 900), (140, 880), (200, 800), (260, 600); step prices 0.5, 1.33, 3.33.


def test_a_limit_between_prices_stops_before_the_first_dearer_step():
    assert go_until(PLANS, 0.6) == (140, 880)


def test_a_limit_below_every_price_stays_at_the_start():
    assert go_until(PLANS, 0.1) == (100, 900)


def test_a_step_priced_at_the_limit_is_taken():
    assert go_until(PLANS, 0.5) == (140, 880)


def test_a_dent_in_the_frontier_does_not_stop_the_walk():
    assert go_until(PLANS, 2.0) == (200, 800)


def test_a_limit_above_every_price_reaches_the_far_end():
    assert go_until(PLANS, 10.0) == (260, 600)
