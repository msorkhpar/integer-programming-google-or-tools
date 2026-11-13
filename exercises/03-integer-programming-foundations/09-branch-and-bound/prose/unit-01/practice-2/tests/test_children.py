import copy

from children import children


def test_a_binary_at_0_4_is_fixed_to_0_and_to_1():
    down, up = children({"open": (0, 1)}, "open", 0.4)
    assert down == {"open": (0, 0)} and up == {"open": (1, 1)}


def test_a_general_integer_splits_at_floor_and_ceiling():
    down, up = children({"trucks": (0, 10)}, "trucks", 3.6)
    assert down == {"trucks": (0, 3)} and up == {"trucks": (4, 10)}


def test_other_variables_keep_their_bounds_in_both_children():
    node = {"open": (0, 1), "trucks": (0, 10), "vans": (0, 2)}
    down, up = children(node, "trucks", 7.2)
    assert down == {"open": (0, 1), "trucks": (0, 7), "vans": (0, 2)}
    assert up == {"open": (0, 1), "trucks": (8, 10), "vans": (0, 2)}


def test_each_child_keeps_the_other_end_of_the_range():
    down, up = children({"trucks": (2, 9)}, "trucks", 4.5)
    assert down == {"trucks": (2, 4)} and up == {"trucks": (5, 9)}


def test_a_negative_value_rounds_down_not_toward_zero():
    down, up = children({"change": (-5, 5)}, "change", -1.5)
    assert down == {"change": (-5, -2)} and up == {"change": (-1, 5)}


def test_the_parent_bounds_are_left_unchanged():
    node = {"open": (0, 1), "trucks": (0, 10)}
    before = copy.deepcopy(node)
    down, up = children(node, "trucks", 2.5)
    assert down["trucks"] == (0, 2) and up["trucks"] == (3, 10)
    assert node == before
