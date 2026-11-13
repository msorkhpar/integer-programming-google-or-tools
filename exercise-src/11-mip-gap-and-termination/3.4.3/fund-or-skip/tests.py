from fund_or_skip import fund_or_skip


def test_a_forced_in_plan_that_beats_every_plan_without_it_means_fund():
    assert fund_or_skip(forced_in=(1_000, 1_010), forced_out=(980, 995)) == "fund"


def test_a_forced_out_plan_that_beats_every_plan_with_it_means_skip():
    assert fund_or_skip(forced_in=(950, 960), forced_out=(990, 1_000)) == "skip"


def test_overlapping_brackets_leave_the_question_open():
    assert fund_or_skip(forced_in=(1_000, 1_020), forced_out=(990, 1_005)) == "undecided"
    assert fund_or_skip(forced_in=(990, 1_005), forced_out=(1_000, 1_020)) == "undecided"


def test_brackets_that_only_touch_leave_the_question_open():
    assert fund_or_skip(forced_in=(1_000, 1_010), forced_out=(985, 1_000)) == "undecided"
    assert fund_or_skip(forced_in=(985, 1_000), forced_out=(1_000, 1_010)) == "undecided"


def test_an_infeasible_forced_in_run_means_skip():
    assert fund_or_skip(forced_in=None, forced_out=(900, 910)) == "skip"


def test_an_infeasible_forced_out_run_means_fund():
    assert fund_or_skip(forced_in=(900, 910), forced_out=None) == "fund"
