import pytest

from npv import npv_table

# A fictional utility's practice portfolio (money in $k). Only the fields the NPV needs are shown.
SNAPSHOT = {
    "years": [2027, 2028, 2029],
    "rate": 0.05,
    "projects": {
        "J1": {"cost": [200, 100], "earliest": 2027, "latest": 2028},
        "J2": {"cost": [150], "earliest": 2027, "latest": 2029},
        "J3": {"cost": [300, 100, 50], "earliest": 2027, "latest": 2027},
        "J4": {"cost": [80], "earliest": 2028, "latest": 2029},
    },
}
# Finance's benefit forecast: a benefit per year of service, from the year after the work ends,
# all smaller by `decay` for each year the start is later than the project's earliest start.
FORECAST = {
    "J1": {"benefits": [90, 90, 90, 90], "decay": 0.05},
    "J2": {"benefits": [40, 40, 40, 40, 40], "decay": 0.10},
    "J3": {"benefits": [200, 150, 100], "decay": 0.0},
    "J4": {"benefits": [30, 30], "decay": 0.02},
}

REFERENCE = {("J1", 2027): 9, ("J1", 2028): -6, ("J2", 2027): 23, ("J2", 2028): 6, ("J2", 2029): -9,
             ("J3", 2027): -66, ("J4", 2028): -23, ("J4", 2029): -23}


def one(cost, earliest, latest, benefits, decay, years=(2027, 2028, 2029)):
    snap = {"years": list(years), "rate": 0.05,
            "projects": {"X": {"cost": cost, "earliest": earliest, "latest": latest}}}
    return npv_table(snap, {"X": {"benefits": benefits, "decay": decay}})


def test_one_whole_k_entry_per_start_and_costs_alone_are_negative():
    table = npv_table(SNAPSHOT, FORECAST)
    assert sorted(table) == sorted(REFERENCE)
    assert all(isinstance(v, int) for v in table.values())
    # Costs only, started in the first plan year: 100 now and 105 next year is -100 - 100.
    assert one([100, 105], 2027, 2027, [], 0.0) == {("X", 2027): -200}


def test_the_whole_table_matches_the_reference():
    # J1's and J3's benefits run past 2029, the plan's last year; they still count.
    assert npv_table(SNAPSHOT, FORECAST) == REFERENCE


def test_every_start_is_discounted_to_the_first_plan_year():
    # The same cash flow started a year later is worth less on the first plan year, by 1.05.
    table = one([100], 2027, 2028, [0], 0.0)
    assert table == {("X", 2027): -100, ("X", 2028): -95}


def test_benefits_begin_the_year_after_the_work_ends():
    # Two years of work in 2027-2028; the single benefit of 221 lands in 2029: 221 / 1.05**2 = 200.5.
    assert one([0, 0], 2027, 2027, [221], 0.0) == {("X", 2027): 200}


def test_delay_is_counted_from_the_projects_own_earliest_start():
    # Earliest start 2028: starting then has no decay (110.25 in 2029 is 100 on 2027),
    # starting in 2029 loses 10% (99.225 in 2030 is 85.7).
    table = one([0], 2028, 2029, [110.25], 0.10)
    assert table == {("X", 2028): 100, ("X", 2029): 86}


def test_a_negative_npv_is_rounded_to_the_nearest_whole_k():
    # -100 + 52.92 / 1.05 = -49.6, which rounds to -50; cutting off the decimals would give -49.
    assert one([100], 2027, 2027, [52.92], 0.0) == {("X", 2027): -50}
