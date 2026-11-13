from verdict import judge, sgm, verdict

BASE_PLAN = [400.0, 900.0, 250.0, 1200.0, 700.0, 300.0]
BASE_PROOF = [9000.0, 15000.0, 4000.0, 22000.0, 12000.0, 6000.0]


def scaled(values, factor):
    return [v * factor for v in values]


def test_a_setting_better_on_both_measures_is_adopted_and_one_worse_is_rejected():
    assert verdict(scaled(BASE_PLAN, 0.6), BASE_PLAN, scaled(BASE_PROOF, 0.8), BASE_PROOF, shift=100) == "adopt"
    assert verdict(BASE_PLAN, BASE_PLAN, scaled(BASE_PROOF, 1.5), BASE_PROOF, shift=100) == "reject"


def test_a_setting_better_on_one_measure_and_worse_on_the_other_is_a_trade_off():
    assert verdict(scaled(BASE_PLAN, 0.4), BASE_PLAN, scaled(BASE_PROOF, 1.5), BASE_PROOF, shift=100) == "trade-off"


def test_a_lower_mean_carried_by_one_run_while_most_runs_lose_is_no_gain():
    new = [v * 1.1 for v in BASE_PROOF[:5]] + [BASE_PROOF[5] / 50]
    assert judge(new, BASE_PROOF, shift=100, margin=0.05) == "same"


def test_a_change_inside_the_margin_is_no_effect():
    assert verdict(scaled(BASE_PLAN, 0.97), BASE_PLAN, scaled(BASE_PROOF, 1.03), BASE_PROOF, shift=100) == "no effect"


def test_the_shift_keeps_tiny_differences_from_counting():
    assert judge([1.0, 1.0, 1700.0], [30.0, 30.0, 1000.0], shift=100, margin=0.05) == "same"


def test_ties_count_as_neither_a_win_nor_a_loss():
    new = [100.0, 100.0, 100.0, 300.0, 300.0]
    old = [100.0, 100.0, 100.0, 1000.0, 1000.0]
    assert judge(new, old, shift=10, margin=0.05) == "better"


def test_a_ratio_exactly_at_the_margin_counts():
    new, old = [600.0, 700.0, 800.0], [800.0, 900.0, 1000.0]
    down = sgm(new, 100) / sgm(old, 100)          # about 0.78, so 1 - (1 - down) == down exactly
    assert judge(new, old, shift=100, margin=1 - down) == "better"
    up = sgm(old, 100) / sgm(new, 100)            # about 1.29, so 1 + (up - 1) == up exactly
    assert judge(old, new, shift=100, margin=up - 1) == "worse"
