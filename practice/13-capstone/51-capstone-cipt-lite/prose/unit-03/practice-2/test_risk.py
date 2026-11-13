import pytest

from risk import risk_table, scale_from_rul

# A fictional utility's practice portfolio (money in $k), and the asset each project works on.
SNAPSHOT = {
    "years": [2027, 2028, 2029],
    "rate": 0.05,
    "projects": {
        "J1": {"cost": [200, 100], "earliest": 2027, "latest": 2028},
        "J2": {"cost": [150], "earliest": 2027, "latest": 2029},
        "J3": {"cost": [80], "earliest": 2028, "latest": 2029},
    },
}
# age and RUL in years; `eta` is the maker's catalog scale; cof in $k; keep: share of age kept after the work.
ASSETS = {
    "J1": {"age": 34, "beta": 3.2, "rul": 8, "eta": 45.0, "cof": 900, "keep": 0.0},
    "J2": {"age": 20, "beta": 2.0, "rul": 25, "eta": 30.0, "cof": 400, "keep": 0.5},
    "J3": {"age": 12, "beta": 1.5, "rul": 20, "eta": 25.0, "cof": 150, "keep": 0.5},
}
REFERENCE = {("J1", 2027): 260.909, ("J1", 2028): 196.82, ("J2", 2027): 15.513, ("J2", 2028): 12.676,
             ("J2", 2029): 9.693, ("J3", 2028): 3.8, ("J3", 2029): 2.944}

# One asset, a two-year plan, a four-year window: age 30, shape 2, RUL 10, catalog scale 40.
ONE = {"X": {"age": 30, "beta": 2.0, "rul": 10, "eta": 40.0, "cof": 100, "keep": 0.0}}


def one(rate):
    snap = {"years": [2027, 2028], "rate": rate, "projects": {"X": {"cost": [1], "earliest": 2027, "latest": 2028}}}
    return risk_table(snap, ONE, window=4)


def test_one_entry_per_start_and_a_later_start_never_removes_more():
    table = risk_table(SNAPSHOT, ASSETS, window=6)
    assert sorted(table) == sorted(REFERENCE)
    assert all(v >= 0 for v in table.values())
    for (pid, t), v in table.items():
        if (pid, t + 1) in table:
            assert v >= table[pid, t + 1]


def test_the_scale_makes_the_rul_the_median():
    assert scale_from_rul(30, 10, 2.0) == pytest.approx(31.7787, abs=1e-4)
    assert risk_table(SNAPSHOT, ASSETS, window=6) == pytest.approx(REFERENCE, abs=1e-3)


def test_after_the_work_the_asset_ages_again():
    # Replaced at the end of 2027: age 0 in 2028, 1 in 2029, 2 in 2030.
    assert one(0.0).get(("X", 2027)) == pytest.approx(18.418, abs=1e-3)


def test_the_window_runs_past_the_plans_last_year():
    # A start in 2028, the plan's last year, still removes risk in 2029 and 2030.
    assert one(0.0).get(("X", 2028)) == pytest.approx(12.675, abs=1e-3)


def test_every_year_is_discounted_to_the_first_plan_year():
    assert one(0.05) == pytest.approx({("X", 2027): 16.719, ("X", 2028): 11.223}, abs=1e-3)
