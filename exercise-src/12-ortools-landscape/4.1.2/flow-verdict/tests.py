from shipping import ship


def test_pallets_take_the_cheapest_path():
    assert ship([(0, 1, 10, 3), (0, 2, 10, 1), (2, 1, 10, 1)], {0: 4, 1: -4}) == 8


def test_a_full_cheap_arc_sends_the_rest_the_long_way():
    # 5 pallets at 2 on the direct lane, then 2 at 4 + 1 through node 2
    assert ship([(0, 1, 5, 2), (0, 2, 5, 4), (2, 1, 5, 1)], {0: 7, 1: -7}) == 20


def test_supplies_that_do_not_balance_are_named():
    assert ship([(0, 1, 10, 2), (0, 2, 10, 3)], {0: 9, 1: -4, 2: -4}) == "UNBALANCED"


def test_arcs_too_small_for_the_supply_are_named():
    assert ship([(0, 1, 3, 2), (0, 2, 3, 1), (2, 1, 1, 1)], {0: 6, 1: -6}) == "INFEASIBLE"
