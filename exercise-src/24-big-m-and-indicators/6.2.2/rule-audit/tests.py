from audit import leaks

BERTH_1 = {"name": "berth_1", "terms": {"ship_a": 4, "ship_b": 3}, "limit": 6, "switch": "tug_1"}
BERTH_2 = {"name": "berth_2", "terms": {"ship_c": 5}, "limit": 5, "switch": "tug_2"}


def test_a_row_broken_through_a_tiny_switch_is_reported():
    values = {"ship_a": 1, "ship_b": 1, "ship_c": 1, "tug_1": 7e-7, "tug_2": 1.0}
    assert leaks(values, [BERTH_1]) == ["berth_1"]
    values["tug_1"] = 1.0
    assert leaks(values, [BERTH_1]) == []


def test_a_switch_below_one_half_counts_as_off():
    values = {"ship_a": 1, "ship_b": 1, "tug_1": 0.4}
    assert leaks(values, [BERTH_1]) == ["berth_1"]


def test_a_total_within_the_tolerance_is_not_a_leak():
    values = {"ship_a": 1, "ship_b": 1, "ship_c": 1.0000000002, "tug_1": 0.0, "tug_2": 0.0}
    assert leaks(values, [BERTH_2, BERTH_1]) == ["berth_1"]


def test_every_leak_is_reported_in_order():
    values = {"ship_a": 1, "ship_b": 1, "ship_c": 2, "tug_1": 1e-9, "tug_2": 2e-9}
    assert leaks(values, [BERTH_2, BERTH_1]) == ["berth_2", "berth_1"]
