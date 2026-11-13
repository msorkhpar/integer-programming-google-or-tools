import itertools

from twins import best_with_cpsat, best_with_highs

# A city's park improvements (not the lesson's portfolio): value points and cost in $k.
VALUE = {"lights": 9, "paths": 7, "toilets": 6, "cafe": 8, "stage": 5, "garden": 4}
COST = {"lights": 40, "paths": 30, "toilets": 35, "cafe": 45, "stage": 25, "garden": 15}


def brute(budget, requires, excludes) -> int:
    best = 0
    for r in range(len(VALUE) + 1):
        for plan in map(set, itertools.combinations(VALUE, r)):
            if (sum(COST[i] for i in plan) <= budget and all(b in plan for a, b in requires if a in plan)
                    and not any(a in plan and b in plan for a, b in excludes)):
                best = max(best, sum(VALUE[i] for i in plan))
    return best


def test_the_budget_alone():
    best = brute(100, [], [])
    assert best_with_cpsat(VALUE, COST, 100, [], []) == best
    assert best_with_highs(VALUE, COST, 100, [], []) == best


def test_a_requirement():
    requires = [("cafe", "toilets"), ("stage", "lights")]
    best = brute(100, requires, [])
    assert best_with_cpsat(VALUE, COST, 100, requires, []) == best
    assert best_with_highs(VALUE, COST, 100, requires, []) == best


def test_two_improvements_that_exclude_each_other():
    excludes = [("lights", "cafe"), ("paths", "garden")]
    best = brute(120, [], excludes)
    assert best_with_cpsat(VALUE, COST, 120, [], excludes) == best
    assert best_with_highs(VALUE, COST, 120, [], excludes) == best
