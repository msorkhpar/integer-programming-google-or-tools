from count import Project, count_allowed


def test_every_plan_that_keeps_the_rules_is_counted():
    bays = [Project("M", 40, must_do=True), Project("A", 30), Project("B", 20, group="G"), Project("C", 25, group="G")]
    assert count_allowed(bays, 100) == 6


def test_the_empty_plan_counts_when_nothing_is_must_do():
    assert count_allowed([Project("A", 30), Project("B", 20)], 40) == 3


def test_a_plan_that_spends_the_budget_exactly_counts():
    bays = [Project("M", 50, must_do=True), Project("A", 30), Project("B", 20)]
    assert count_allowed(bays, 100) == 4


def test_a_parent_alone_is_allowed_and_a_child_alone_is_not():
    assert count_allowed([Project("P", 30), Project("K", 20, parent="P")], 100) == 3
