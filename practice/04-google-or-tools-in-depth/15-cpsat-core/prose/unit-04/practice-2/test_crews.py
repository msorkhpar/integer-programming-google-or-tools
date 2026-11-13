import itertools

from crews import Job, best_order

# A drainage contractor's culvert repairs (not the lesson's circuits).
OVERDUE = [Job("A", 3, 2, 4), Job("B", 2, 1, 1), Job("C", 4, 3, 3), Job("D", 1, 0, 2), Job("E", 2, 1, 5)]
RELAXED = [Job("P", 2, 10, 3), Job("Q", 3, 12, 1), Job("R", 1, 4, 2), Job("S", 2, 3, 4)]


def cost_of(order: list[str], jobs: list[Job]) -> int:
    by_name = {j.name: j for j in jobs}
    day, total = 0, 0
    for name in order:
        day += by_name[name].days
        total += by_name[name].weight * max(0, day - by_name[name].due)
    return total


def brute(jobs: list[Job]) -> int:
    return min(cost_of([j.name for j in perm], jobs) for perm in itertools.permutations(jobs))


def test_the_least_weighted_lateness():
    cost, _ = best_order(OVERDUE)
    assert cost == brute(OVERDUE)


def test_the_order_achieves_the_cost():
    cost, order = best_order(OVERDUE)
    assert sorted(order) == sorted(j.name for j in OVERDUE)
    assert cost_of(order, OVERDUE) == cost == brute(OVERDUE)


def test_finishing_early_earns_nothing():
    cost, order = best_order(RELAXED)
    assert cost == brute(RELAXED)
    assert cost_of(order, RELAXED) == cost
