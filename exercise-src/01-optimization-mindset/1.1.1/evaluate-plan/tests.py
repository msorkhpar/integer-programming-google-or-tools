from plans import Project, evaluate_plan

# A substation portfolio unlike the lesson's: costs and values in $k.
YARD = [
    Project("S1", 400, 520, must_do=True),
    Project("S2", 250, 300, must_do=True),
    Project("S3", 300, 410),
    Project("S4", 150, 260, parent="S3"),
    Project("S5", 200, 330, group="breakers"),
    Project("S6", 90, 120, group="breakers"),
    Project("S7", 60, 75),
]


def test_an_allowed_plan_has_its_value_and_no_problems():
    value, problems = evaluate_plan(YARD, 1_300, {"S1", "S2", "S3", "S4", "S6"})
    assert value == 1610
    assert problems == []


def test_spending_exactly_the_budget_is_allowed():
    value, problems = evaluate_plan(YARD, 1_190, {"S1", "S2", "S3", "S4", "S6"})
    assert problems == []


def test_must_do_cost_counts_against_the_budget():
    value, problems = evaluate_plan(YARD, 700, {"S1", "S2", "S6"})
    assert problems == ["budget"]


def test_every_must_do_is_required():
    value, problems = evaluate_plan(YARD, 2_000, {"S1", "S7"})
    assert sorted(problems) == ["must-do:S2"]


def test_a_parent_may_be_funded_alone():
    value, problems = evaluate_plan(YARD, 2_000, {"S1", "S2", "S3"})
    assert problems == []


def test_a_child_without_its_parent_is_reported():
    value, problems = evaluate_plan(YARD, 2_000, {"S1", "S2", "S4"})
    assert problems == ["parent:S4"]


def test_funding_neither_alternative_is_allowed():
    value, problems = evaluate_plan(YARD, 2_000, {"S1", "S2", "S7"})
    assert problems == []
    assert value == 895


def test_two_alternatives_from_one_group_are_reported():
    value, problems = evaluate_plan(YARD, 2_000, {"S1", "S2", "S5", "S6"})
    assert problems == ["alternatives:breakers"]
