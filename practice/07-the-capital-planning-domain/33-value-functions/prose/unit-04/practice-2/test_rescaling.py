from rescaling import ranking, survives_rescaling

# Two measures: rider time saved and cost saved. A normalized value and a raw sum, to be tested.
REFERENCE = {"time": 3.0, "cost": 7.0}


def normalized(benefit, reference):
    return 0.5 * benefit["time"] / reference["time"] + 0.5 * benefit["cost"] / reference["cost"]


def raw_sum(benefit, reference):
    return benefit["time"] + benefit["cost"]


PROJECTS = {
    "North": {"time": 2.4, "cost": 0.5},
    "South": {"time": 0.3, "cost": 6.0},
    "East": {"time": 1.2, "cost": 2.0},
}
HOURS_TO_MINUTES_AND_DOLLARS_TO_K = {"time": 60.0, "cost": 0.001}


def test_rankings_are_listed_from_the_highest_value():
    assert ranking({"a": 0.2, "b": 0.7, "c": 0.4}) == ["b", "c", "a"]
    assert ranking({"x": 1.0, "w": 1.0, "v": 3.0}) == ["v", "w", "x"]


def test_a_normalized_value_survives_and_a_raw_sum_does_not():
    assert survives_rescaling(normalized, PROJECTS, REFERENCE, HOURS_TO_MINUTES_AND_DOLLARS_TO_K) is True
    assert survives_rescaling(raw_sum, PROJECTS, REFERENCE, HOURS_TO_MINUTES_AND_DOLLARS_TO_K) is False


def test_a_change_below_the_top_place_is_a_change():
    lines = {"Main": {"time": 8.0, "cost": 1.0}, "Loop": {"time": 1.0, "cost": 4.0}, "Spur": {"time": 2.0, "cost": 2.5}}
    factors = {"time": 1.0, "cost": 0.1}               # raw sums 9.0, 5.0, 4.5 -> 8.1, 1.4, 2.25
    assert survives_rescaling(raw_sum, lines, REFERENCE, factors) is False
    assert survives_rescaling(normalized, lines, REFERENCE, factors) is True


def test_values_equal_up_to_rounding_are_a_tie():
    twins = {"Pine": {"time": 0.4, "cost": 6.4}, "Elm": {"time": 2.8, "cost": 0.8}}   # both 11/21
    factors = {"time": 60.0, "cost": 0.001}
    assert ranking({"Pine": 11 / 21 + 1e-16, "Elm": 11 / 21}) == ["Elm", "Pine"]
    assert survives_rescaling(normalized, twins, REFERENCE, factors) is True
    assert survives_rescaling(raw_sum, twins, REFERENCE, factors) is False


def test_near_ties_chain_into_one_group():
    values = {"c": 1.0, "b": 1.0 - 0.6e-9, "a": 1.0 - 1.2e-9}       # each within TIED of the next
    assert ranking(values) == ["a", "b", "c"]
