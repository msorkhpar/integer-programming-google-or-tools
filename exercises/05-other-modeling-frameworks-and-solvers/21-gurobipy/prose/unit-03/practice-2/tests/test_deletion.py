from deletion import deletion_filter


def interval_check(limits):
    """Rules are bounds on one load x: (lower, upper); a set holds if its largest lower <= smallest upper."""
    calls = []

    def feasible(subset):
        calls.append(frozenset(subset))
        low = max([limits[r][0] for r in subset if limits[r][0] is not None], default=0)
        high = min([limits[r][1] for r in subset if limits[r][1] is not None], default=float("inf"))
        return low <= high
    return feasible, calls


def test_two_clashing_rules_are_kept_and_the_rest_dropped():
    limits = {"order_min": (5, None), "axle_max": (None, 3), "deck_max": (None, 10), "floor": (0, None)}
    feasible, _ = interval_check(limits)
    assert deletion_filter(list(limits), feasible) == ["order_min", "axle_max"]


def test_the_rules_come_back_in_their_given_order():
    limits = {"deck_max": (None, 10), "axle_max": (None, 3), "floor": (0, None), "order_min": (5, None)}
    feasible, _ = interval_check(limits)
    assert deletion_filter(list(limits), feasible) == ["axle_max", "order_min"]


def test_a_dropped_rule_stays_dropped():
    limits = {"order_min": (5, None), "axle_max": (None, 3), "bridge_max": (None, 4)}
    feasible, _ = interval_check(limits)
    assert deletion_filter(list(limits), feasible) == ["order_min", "bridge_max"]


def test_a_feasible_set_has_no_conflict():
    limits = {"order_min": (2, None), "axle_max": (None, 3), "deck_max": (None, 10)}
    feasible, _ = interval_check(limits)
    assert deletion_filter(list(limits), feasible) == []
