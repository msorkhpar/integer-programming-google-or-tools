from next_node import next_node


def test_depth_first_takes_the_deepest_node():
    assert next_node([(1, 1, 90.0), (4, 3, 70.0), (3, 2, 80.0)], "depth") == 4


def test_best_first_takes_the_highest_bound():
    assert next_node([(1, 1, 90.0), (4, 3, 70.0), (3, 2, 80.0)], "best") == 1


def test_breadth_first_takes_the_oldest_node():
    assert next_node([(2, 1, 60.0), (5, 3, 95.0), (7, 3, 75.0)], "breadth") == 2


def test_best_first_ties_go_to_the_older_node():
    assert next_node([(4, 2, 88.0), (6, 3, 88.0), (7, 3, 61.0)], "best") == 4
    assert next_node([(9, 3, 88.0), (8, 2, 88.0)], "best") == 8


def test_depth_first_ties_go_to_the_newer_node():
    assert next_node([(10, 4, 50.0), (11, 4, 49.0), (3, 2, 70.0)], "depth") == 11
    assert next_node([(12, 4, 50.0), (11, 4, 49.0)], "depth") == 12


def test_the_waiting_list_may_be_in_any_order():
    assert next_node([(9, 4, 40.0), (2, 1, 55.0), (6, 3, 47.0)], "breadth") == 2
