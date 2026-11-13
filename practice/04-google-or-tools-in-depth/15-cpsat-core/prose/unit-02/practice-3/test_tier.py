from ortools.sat.python import cp_model

from tier import add_tier_flag

THRESHOLD = 500      # a test retailer's gold tier, in dollars


def allowed(spend: int, gold: bool, threshold: int = THRESHOLD) -> bool:
    model = cp_model.CpModel()
    s = model.new_int_var(0, 1_000, "spend")
    g = model.new_bool_var("gold")
    add_tier_flag(model, s, g, threshold)
    model.add(s == spend)
    model.add(g == int(gold))
    return cp_model.CpSolver().solve(model) == cp_model.OPTIMAL


def test_a_big_spender_is_gold():
    assert allowed(650, True) is True
    assert allowed(650, False) is False


def test_a_small_spender_is_not_gold():
    assert allowed(320, False) is True
    assert allowed(320, True) is False


def test_spending_exactly_the_threshold_is_gold():
    assert allowed(500, True) is True
    assert allowed(500, False) is False


def test_the_flag_follows_the_threshold_it_is_given():
    assert allowed(650, False, threshold=800) is True
    assert allowed(650, True, threshold=800) is False
