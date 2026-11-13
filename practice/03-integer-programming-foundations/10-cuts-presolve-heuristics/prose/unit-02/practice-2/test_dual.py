from dual import dual_fixings


def test_a_valuable_variable_in_no_row_is_fixed_at_one():
    assert dual_fixings({"a": 5, "b": 3, "c": 4}, {"r1": ({"a": 2, "b": 3}, 4)}) == {"c": 1}


def test_a_parent_with_only_a_negative_entry_is_fixed_at_one():
    rows = {"after": ({"child": 1, "parent": -1}, 0), "cap": ({"child": 3, "d": 2}, 4)}
    assert dual_fixings({"child": 4, "parent": 1, "d": 2}, rows) == {"parent": 1}


def test_a_costly_variable_with_only_positive_entries_is_fixed_at_zero():
    rows = {"hours": ({"shift": 1, "job": 2}, 2)}
    assert dual_fixings({"shift": -2, "job": 3}, rows) == {"shift": 0}


def test_every_row_of_a_variable_counts():
    rows = {"r1": ({"a": -1, "b": 1}, 0), "r2": ({"a": 2}, 1)}
    assert dual_fixings({"a": 5, "b": 1, "e": 2}, rows) == {"e": 1}


def test_a_variable_worth_zero_is_fixed_at_one_only_if_no_entry_is_positive():
    rows = {"r": ({"z": -1, "w": 2}, 3)}
    assert dual_fixings({"z": 0, "w": 0, "u": 0}, rows) == {"z": 1, "u": 1}
