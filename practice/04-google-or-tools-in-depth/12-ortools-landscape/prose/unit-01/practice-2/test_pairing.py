import itertools

from pairing import pair


def cheapest(hours):
    """The least total over every pairing that uses cleared pairs only, or None."""
    n, best = len(hours), None
    for depots in itertools.permutations(range(n)):
        if all(hours[k][depots[k]] is not None for k in range(n)):
            total = sum(hours[k][depots[k]] for k in range(n))
            best = total if best is None else min(best, total)
    return best


def check(hours):
    answer = pair(hours)
    assert answer is not None
    total, depot_of = answer
    assert sorted(depot_of) == list(range(len(hours))), "every depot gets exactly one crew"
    assert all(hours[k][d] is not None for k, d in enumerate(depot_of)), "a crew went where it is not cleared"
    assert total == sum(hours[k][d] for k, d in enumerate(depot_of)) == cheapest(hours)
    return depot_of


def test_three_crews_get_the_cheapest_pairing():
    check([[6, 2, 9], [3, 8, 4], [5, 7, 1]])


def test_the_cheapest_pairing_is_not_each_crews_nearest():
    depot_of = check([[1, 4, 6, 9], [2, 7, 8, 5], [3, 6, 2, 8], [4, 9, 7, 6]])
    assert depot_of[0] != 0                        # crew 0's nearest depot goes to another crew


def test_a_pair_marked_none_is_never_used():
    check([[None, 5, 6], [4, 1, 7], [3, 6, 2]])


def test_no_full_pairing_gives_none():
    assert pair([[1, None, 2], [3, None, 4], [5, None, 6]]) is None
