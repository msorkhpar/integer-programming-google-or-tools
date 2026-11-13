from fleet_finance import finance_text

RUN = {"budget": {2027: 11000, 2028: 12500}, "spend": {2027: 10850, 2028: 12500},
       "npv": 30412.4, "bound": 30412.4, "status": "OPTIMAL"}


def test_each_year_then_the_proven_value():
    assert finance_text(RUN) == [
        "2027: spend 10,850 of 11,000, 150 left",
        "2028: spend 12,500 of 12,500, 0 left",
        "NPV $30,412k, proven optimal",
    ]


def test_a_year_over_its_budget_is_marked():
    run = {**RUN, "spend": {2027: 11200, 2028: 12500}}
    assert finance_text(run)[:1] == ["2027: spend 11,200 of 11,000, OVER by 200"]


def test_years_come_oldest_first_whatever_the_record_s_order():
    run = {**RUN, "budget": {2028: 12500, 2027: 11000}}
    assert [line[:4] for line in finance_text(run)[:2]] == ["2027", "2028"]


def test_a_run_that_stopped_early_is_not_proven():
    run = {**RUN, "npv": 29950.0, "bound": 30600.2, "status": "FEASIBLE"}
    assert finance_text(run)[-1:] == ["NPV $29,950k, not proven: no plan is worth more than $30,600k"]


def test_an_optimal_status_with_a_gap_left_is_not_proven():
    run = {**RUN, "npv": 30412.4, "bound": 30700.0, "status": "OPTIMAL"}
    assert finance_text(run)[-1:] == ["NPV $30,412k, not proven: no plan is worth more than $30,700k"]


def test_float_amounts_are_rounded_to_whole_k_before_comparing():
    run = {**RUN, "budget": {2027: 11000.0, 2028: 12500.0}, "spend": {2027: 10849.6, 2028: 12500.4}}
    assert finance_text(run)[:2] == [
        "2027: spend 10,850 of 11,000, 150 left",
        "2028: spend 12,500 of 12,500, 0 left",
    ]
