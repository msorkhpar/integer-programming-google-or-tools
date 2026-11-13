from cumulative import cumulative_check

BUDGET = {2027: 400, 2028: 400, 2029: 400}


def job(cost, deadline, required=True):
    return {"cost": cost, "deadline": deadline, "required": required}


def test_a_year_whose_due_work_outruns_the_money_so_far_is_reported():
    fits = {"main-1": job(100, 2027), "main-2": job(200, 2028), "main-3": job(100, 2029)}
    assert cumulative_check(fits, BUDGET) == []
    late = {"main-1": job(100, 2027), "main-2": job(200, 2028), "main-3": job(1000, 2029)}
    assert [(year, due) for year, due, _ in cumulative_check(late, BUDGET)] == [(2029, 1300)]


def test_every_year_that_falls_short_is_reported():
    early = {"reservoir": job(900, 2027)}
    assert cumulative_check(early, BUDGET) == [(2027, 900, 400), (2028, 900, 800)]


def test_money_left_over_carries_into_later_years():
    # 2028's work alone is more than 2028's budget, but 2027's unspent money pays for it.
    carried = {"meter": job(100, 2027), "tank": job(600, 2028)}
    assert cumulative_check(carried, BUDGET) == []
    assert cumulative_check({"meter": job(300, 2027), "tank": job(600, 2028)}, BUDGET) == [(2028, 900, 800)]


def test_optional_work_is_never_due():
    optional = {"main-1": job(300, 2027), "paint": job(900, 2027, required=False)}
    assert cumulative_check(optional, BUDGET) == []
    assert cumulative_check({**optional, "pipe": job(150, 2027)}, BUDGET) == [(2027, 450, 400)]
