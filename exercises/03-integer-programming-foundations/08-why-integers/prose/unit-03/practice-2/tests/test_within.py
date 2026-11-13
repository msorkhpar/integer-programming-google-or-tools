from within import count_within


def test_each_subset_within_the_budget_is_counted_once_including_the_empty_one():
    assert count_within([60, 70, 80], 100) == 4
    assert count_within([], 50) == 1


def test_a_project_joins_a_plan_at_most_once():
    assert count_within([30, 40], 100) == 4
    assert count_within([10, 20, 30], 60) == 8


def test_a_subset_that_costs_exactly_the_budget_counts():
    assert count_within([30, 40], 70) == 4
