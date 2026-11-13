from swaps import pair_swaps

GROUPS = {"reline_M4": "main_4", "replace_M4": "main_4", "reline_M9": "main_9", "replace_M9": "main_9"}


def test_a_swap_inside_a_group_is_one_change():
    assert pair_swaps(["reline_M4", "valve_V2"], ["replace_M4"], GROUPS) == {
        "swaps": [("replace_M4", "reline_M4")], "adds": ["valve_V2"], "drops": []}


def test_a_dropped_option_with_nothing_added_in_its_group_stays_a_drop():
    assert pair_swaps(["valve_V2"], ["replace_M9"], GROUPS) == {
        "swaps": [], "adds": ["valve_V2"], "drops": ["replace_M9"]}


def test_projects_without_a_group_never_pair():
    assert pair_swaps(["valve_V2"], ["hydrant_H7"], GROUPS) == {
        "swaps": [], "adds": ["valve_V2"], "drops": ["hydrant_H7"]}


def test_swaps_are_listed_by_the_dropped_option():
    assert pair_swaps(["reline_M4", "replace_M9"], ["replace_M4", "reline_M9"], GROUPS)["swaps"] == [
        ("reline_M9", "replace_M9"), ("replace_M4", "reline_M4")]
