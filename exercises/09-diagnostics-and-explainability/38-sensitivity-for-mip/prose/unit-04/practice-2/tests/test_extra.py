from extra import what_extra_buys

CURVE = [(100, 40), (130, 52), (150, 70), (210, 81)]


def test_extra_money_inside_a_flat_stretch():
    assert what_extra_buys(CURVE, 120, 40) == {"gain": 30, "steps": 2, "next": (130, 12)}
    assert what_extra_buys(CURVE, 220, 50) == {"gain": 0, "steps": 0, "next": None}


def test_a_budget_exactly_at_a_step_stands_on_it():
    assert what_extra_buys(CURVE, 130, 20)["gain"] == 18


def test_the_next_step_lies_strictly_above_the_budget():
    assert what_extra_buys(CURVE, 150, 100)["next"] == (210, 11)


def test_a_budget_below_the_curve_has_no_answer():
    assert what_extra_buys(CURVE, 90, 50) is None
