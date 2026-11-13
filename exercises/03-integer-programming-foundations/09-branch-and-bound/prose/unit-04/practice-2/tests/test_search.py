import random

from search import best_plan


def brute_force(items, budget, must):
    best = None
    for mask in range(1 << len(items)):
        chosen = [it for k, it in enumerate(items) if mask >> k & 1]
        names = {n for n, _, _ in chosen}
        if must <= names and sum(c for _, _, c in chosen) <= budget:
            value = sum(v for _, v, _ in chosen)
            if best is None or value > best:
                best = value
    return best


def test_a_small_instance_by_hand():
    items = [("A", 60, 10), ("B", 100, 20), ("C", 120, 30), ("D", 70, 50), ("E", 30, 40)]
    assert best_plan(items, 50, set()) == (220, ["B", "C"])
    assert best_plan(items, 100, set()) == (310, ["A", "B", "C", "E"])


def test_twenty_random_instances_match_brute_force():
    for seed in range(20):
        rng = random.Random(seed)
        items = [(f"s{k}", rng.randint(1, 60), rng.randint(1, 40)) for k in range(12)]
        budget = sum(c for _, _, c in items) // 2
        value, names = best_plan(items, budget, set())
        assert value == brute_force(items, budget, set()), f"seed {seed}"
        chosen = [it for it in items if it[0] in names]
        assert sum(c for _, _, c in chosen) <= budget and sum(v for _, v, _ in chosen) == value


def test_must_stock_items_are_in_the_plan_and_its_value():
    items = [("A", 60, 10), ("B", 100, 20), ("C", 120, 30), ("R", 5, 25)]
    assert best_plan(items, 60, {"R"}) == (165, ["A", "B", "R"])
    assert best_plan(items, 60, {"R"})[0] == brute_force(items, 60, {"R"})


def test_must_stock_items_over_budget_give_none():
    items = [("A", 60, 10), ("R", 5, 25), ("Q", 8, 30)]
    assert best_plan(items, 50, {"R", "Q"}) is None
    assert best_plan(items, 55, {"R", "Q"}) == (13, ["Q", "R"])
