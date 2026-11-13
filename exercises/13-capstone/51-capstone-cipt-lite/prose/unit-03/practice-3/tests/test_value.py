import pytest

from value import REFERENCE, value_table, ranking, weights

# Three measures for each start of a fictional utility's practice portfolio: NPV ($k), risk removed
# ($k) and customer-minutes of outage avoided.
MEASURES = {
    "npv": {("J1", 2027): 300, ("J1", 2028): 260, ("J2", 2027): 90, ("J3", 2028): 400, ("J4", 2027): 0},
    "risk": {("J1", 2027): 40.0, ("J1", 2028): 35.0, ("J2", 2027): 180.0, ("J3", 2028): 10.0, ("J4", 2027): 0.0},
    "minutes": {("J1", 2027): 20_000, ("J1", 2028): 18_000, ("J2", 2027): 5_000, ("J3", 2028): 0, ("J4", 2027): 0},
}
EXPECTED = {("J1", 2027): 0.3, ("J1", 2028): 0.262917, ("J2", 2027): 0.436667,
            ("J3", 2028): 0.220833, ("J4", 2027): 0.0}


def test_one_value_per_start_and_the_ranking_goes_down():
    table = value_table(MEASURES)
    assert sorted(table) == sorted(EXPECTED)
    assert table[("J4", 2027)] == 0.0
    order = ranking(table)
    assert sorted(order) == sorted(EXPECTED)
    assert all(table[a] >= table[b] for a, b in zip(order, order[1:]))


def test_weights_are_the_ratings_over_their_total():
    assert weights({"risk": 100, "minutes": 80, "npv": 60}) == pytest.approx(
        {"risk": 100 / 240, "minutes": 80 / 240, "npv": 60 / 240})


def test_the_table_matches_the_reference():
    assert value_table(MEASURES) == pytest.approx(EXPECTED, abs=1e-6)


def test_withdrawing_a_project_leaves_the_other_values_alone():
    without = {k: {key: v for key, v in table.items() if key[0] != "J2"} for k, table in MEASURES.items()}
    table = value_table(without)
    assert table == pytest.approx({key: v for key, v in EXPECTED.items() if key[0] != "J2"}, abs=1e-6)


def test_restating_risk_in_millions_with_its_reference_changes_nothing():
    in_millions = {**MEASURES, "risk": {key: v / 1000 for key, v in MEASURES["risk"].items()}}
    reference = {**REFERENCE, "risk": REFERENCE["risk"] / 1000}
    table = value_table(in_millions, reference)
    assert table == pytest.approx(EXPECTED, abs=1e-6)
    assert ranking(table) == ranking(EXPECTED)


def test_equal_values_are_ranked_in_key_order():
    assert ranking({("J9", 2028): 0.5, ("J2", 2029): 0.7, ("J5", 2027): 0.5}) == [
        ("J2", 2029), ("J5", 2027), ("J9", 2028)]
