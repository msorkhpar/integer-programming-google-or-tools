from cs import cs_violations

# A bakery's day: trays of bread, cakes and pastries, profit per tray.
VALUE = {"bread": 4, "cake": 3, "pastry": 2}
OVEN = ({"bread": 1, "cake": 1, "pastry": 1}, "<=", 10)       # oven slots
FLOUR = ({"bread": 1}, "<=", 6)                               # bread flour, in trays
ROWS = {"oven": OVEN, "flour": FLOUR}
PRICES = {"oven": 3, "flour": 1}


def test_the_optimal_pair_passes_and_other_plans_are_flagged():
    assert cs_violations(VALUE, ROWS, {"bread": 6, "cake": 4, "pastry": 0}, PRICES) == []
    assert cs_violations(VALUE, ROWS, {"bread": 5, "cake": 4, "pastry": 0}, PRICES) == ["flour", "oven"]
    assert cs_violations(VALUE, ROWS, {"bread": 6, "cake": 3, "pastry": 1}, PRICES) == ["pastry"]


def test_rounding_noise_is_not_a_violation():
    noisy = {"bread": 6 - 3e-9, "cake": 4 + 2e-9, "pastry": 4e-10}
    assert cs_violations(VALUE, ROWS, noisy, {"oven": 3 + 1e-9, "flour": 1}) == []
    assert cs_violations(VALUE, ROWS, {"bread": 6, "cake": 4 - 1e-3, "pastry": 1e-3}, PRICES) == ["pastry"]


def test_a_minimum_with_room_above_it_must_have_price_zero():
    rows = {**ROWS, "min_cake": ({"cake": 1}, ">=", 5)}
    prices = {"oven": 4, "flour": 0, "min_cake": -1}
    assert cs_violations(VALUE, rows, {"bread": 5, "cake": 5, "pastry": 0}, prices) == []
    assert cs_violations(VALUE, rows, {"bread": 4, "cake": 6, "pastry": 0}, prices) == ["min_cake"]


def test_a_reduced_cost_counts_every_row_the_activity_is_in():
    rows = {**ROWS, "min_cake": ({"cake": 1}, ">=", 5)}
    prices = {"oven": 4, "flour": 0, "min_cake": -1}
    assert cs_violations(VALUE, rows, {"bread": 5, "cake": 5, "pastry": 0}, prices) == []
    assert cs_violations(VALUE, rows, {"bread": 4, "cake": 5, "pastry": 1}, prices) == ["pastry"]
