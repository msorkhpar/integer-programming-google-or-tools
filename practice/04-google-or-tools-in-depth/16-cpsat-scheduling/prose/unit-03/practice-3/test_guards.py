from guards import plan_nights


def check(guards, need, cost, forbidden, total, at):
    """Assert the roster keeps every rule and costs `total`."""
    n, nights = len(cost), len(need)
    assert set(at) == {(g, d) for g in guards for d in range(nights)}
    for d in range(nights):
        for p in range(n - 1):
            assert sum(at[g, d] == p for g in guards) == need[d].get(p, 0), f"night {d}, place {p}"
    paid = 0
    for g in guards:
        for d in range(nights - 1):
            move = (at[g, d], at[g, d + 1])
            assert move not in forbidden, f"{g} makes the forbidden move {move} after night {d}"
            paid += cost[move[0]][move[1]]
    assert total == paid


SYMMETRIC = [[0, 2, 1], [2, 0, 1], [1, 1, 0]]


def test_staying_put_costs_nothing():
    need = [{0: 1, 1: 1}] * 3
    total, at = plan_nights(["ana", "ben"], need, SYMMETRIC, [])
    check(["ana", "ben"], need, SYMMETRIC, [], total, at)
    assert total == 0


def test_every_guard_has_a_place_each_night():
    need = [{0: 1}, {1: 1}]
    total, at = plan_nights(["ana", "ben"], need, SYMMETRIC, [])
    check(["ana", "ben"], need, SYMMETRIC, [], total, at)
    assert total == 2


def test_a_move_costs_the_from_to_entry():
    cost = [[0, 1, 3], [9, 0, 3], [3, 3, 0]]          # 0 -> 1 costs 1, but 1 -> 0 costs 9
    need = [{0: 1}, {1: 1}]
    # The guard at 0 walks over to 1 for 1; going home and calling the other guard in costs 6.
    total, at = plan_nights(["ana", "ben"], need, cost, [])
    check(["ana", "ben"], need, cost, [], total, at)
    assert total == 1


def test_a_forbidden_move_never_happens():
    cost = [[0, 1, 2], [1, 0, 2], [2, 2, 0]]
    need = [{0: 1}, {1: 1}]
    forbidden = [(0, 1)]
    total, at = plan_nights(["ana", "ben"], need, cost, forbidden)
    check(["ana", "ben"], need, cost, forbidden, total, at)
    # The guard at 0 goes home (2) and the other comes in from home to 1 (2).
    assert total == 4
