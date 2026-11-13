from fleet import carry_forward, committed

OLD = {"B1": 2027, "B2": 2029, "B3": 2028, "B4": 2030}
WINDOWS = {"B2": [2028, 2029, 2030], "B3": [2028, 2029], "B4": [2028, 2029], "B9": [2028, 2029]}


def test_each_kept_replacement_is_hinted_in_its_old_year():
    start = carry_forward(OLD, WINDOWS, 2027)
    assert start.get(("B2", 2029)) == 1.0 and start.get(("B3", 2028)) == 1.0
    assert start.get(("B2", 2028), 0.0) == 0.0 and start.get(("B2", 2030), 0.0) == 0.0
    assert start.get(("B3", 2029), 0.0) == 0.0


def test_the_buses_planned_for_the_year_that_began_are_committed():
    assert committed(OLD, 2027) == {"B1"}
    assert committed({"B5": 2031}, 2027) == set()


def test_every_variable_gets_a_value_so_the_start_is_complete():
    start = carry_forward(OLD, WINDOWS, 2027)
    assert set(start) == {(b, y) for b, years in WINDOWS.items() for y in years}


def test_a_new_bus_is_hinted_zero_in_every_year():
    start = carry_forward(OLD, WINDOWS, 2027)
    assert start.get(("B9", 2028)) == 0.0 and start.get(("B9", 2029)) == 0.0


def test_an_old_year_outside_the_new_window_hints_no_year():
    start = carry_forward(OLD, WINDOWS, 2027)
    assert start.get(("B4", 2028)) == 0.0 and start.get(("B4", 2029)) == 0.0


def test_a_committed_bus_still_in_the_windows_is_not_hinted_again():
    windows = {"B1": [2027, 2028], "B2": [2029]}
    start = carry_forward({"B1": 2027, "B2": 2029}, windows, 2027)
    assert start.get(("B1", 2027)) == 0.0 and start.get(("B2", 2029)) == 1.0
