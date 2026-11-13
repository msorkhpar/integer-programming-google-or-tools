import itertools

from inspection import separate_floor

# A pipeline operator's inspection programme, not the lesson's portfolio.


def valid(km, floor, chosen_set) -> bool:
    """Every whole plan meeting the floor includes a line of the set."""
    for plan in itertools.product((0, 1), repeat=len(km)):
        taken = {i for i, t in zip(km, plan) if t}
        if sum(km[i] for i in taken) >= floor and not taken & set(chosen_set):
            return False
    return True


def test_a_line_every_plan_needs_is_found():
    km = {"Trunk": 10, "Spur1": 3, "Spur2": 2}
    # The spurs add only 5 km, so every plan reaching 7 km inspects Trunk; the LP point does 0.4 of it.
    xstar = {"Trunk": 0.4, "Spur1": 0.6, "Spur2": 0.6}
    found = separate_floor(km, 7, xstar)
    assert found is not None
    assert valid(km, 7, found)
    assert sum(xstar[i] for i in found) < 1


def test_a_whole_plan_breaks_no_such_row():
    km = {"A": 6, "B": 5, "C": 4, "D": 3}
    assert separate_floor(km, 9, {"A": 1.0, "B": 0.0, "C": 1.0, "D": 0.0}) is None
    km = {"Main": 12, "Loop": 4, "Tap": 3}
    xstar = {"Main": 0.5, "Loop": 0.75, "Tap": 1.0}
    found = separate_floor(km, 9, xstar)
    assert found is not None and valid(km, 9, found) and sum(xstar[i] for i in found) < 1


def test_lengths_outside_the_set_must_fall_short_of_the_floor():
    km = {"A": 5, "B": 3, "C": 2}
    # B + C reach exactly 5 km, so a plan without A can meet the floor: "A is needed" is not valid.
    assert separate_floor(km, 5, {"A": 0.3, "B": 1.0, "C": 1.0}) is None
    found = separate_floor(km, 6, {"A": 0.3, "B": 1.0, "C": 1.0})
    assert found is not None and valid(km, 6, found)


def test_the_set_the_lp_point_under_uses_is_found():
    km = {"A": 6, "B": 6, "C": 6}
    xstar = {"A": 0.1, "B": 0.1, "C": 1.0}                       # 0.6 + 0.6 + 6 = 7.2 km for a floor of 7
    found = separate_floor(km, 7, xstar)
    assert found is not None and sorted(found) == ["A", "B"]
    assert valid(km, 7, found)
