from raises import smallest_raise

COST = {"R12": 700, "R31": 600, "R07": 300}


def test_jobs_fixed_to_one_year_need_their_excess_over_that_year():
    assert smallest_raise({"R12": [2027], "R31": [2027]}, COST, {2027: 1000, 2028: 0}) == (300, {"R12": 2027, "R31": 2027})
    assert smallest_raise({"R12": [2027], "R31": [2028]}, COST, {2027: 1000, 2028: 1000}) == (0, {"R12": 2027, "R31": 2028})


def test_the_cheapest_combination_of_years_is_chosen():
    # R12 in 2027 overruns by 300; moved to 2028 it overruns by only 100.
    years = {"R12": [2027, 2028], "R31": [2027]}
    assert smallest_raise(years, COST, {2027: 1000, 2028: 600}) == (100, {"R12": 2028, "R31": 2027})


def test_shortfalls_in_different_years_add_up():
    years = {"R12": [2027], "R31": [2028], "R07": [2028]}
    assert smallest_raise(years, COST, {2027: 500, 2028: 800}) == (300, {"R12": 2027, "R31": 2028, "R07": 2028})


def test_room_in_one_year_does_not_cover_another():
    years = {"R12": [2027], "R31": [2028]}
    assert smallest_raise(years, COST, {2027: 500, 2028: 2000}) == (200, {"R12": 2027, "R31": 2028})
