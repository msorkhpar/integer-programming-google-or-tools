from rows import Project, broken_rows

MAINS = [
    Project("M1", 40, 55, must_do=True),
    Project("M2", 30, 42),
    Project("M3", 30, 36, parent="M2"),
    Project("M4", 20, 26, group="G1"),
    Project("M5", 15, 24, group="G1"),
]


def test_each_broken_row_is_named_by_its_label():
    assert broken_rows({"M1", "M2", "M3", "M4", "M5"}, MAINS, 100) == {"budget", "alt_G1"}
    assert broken_rows({"M2", "M3"}, MAINS, 100) == {"must_M1"}
    assert broken_rows({"M3", "M4", "M5"}, MAINS, 100) == {"must_M1", "parent_M3", "alt_G1"}


def test_a_plan_that_spends_the_budget_exactly_is_within_it():
    assert broken_rows({"M1", "M2", "M3"}, MAINS, 100) == set()
    assert broken_rows({"M1", "M2", "M3", "M5"}, MAINS, 100) == {"budget"}


def test_a_parent_without_its_child_is_allowed_and_a_child_without_its_parent_is_not():
    assert broken_rows({"M1", "M2"}, MAINS, 100) == set()
    assert broken_rows({"M1", "M3"}, MAINS, 100) == {"parent_M3"}


def test_one_project_of_an_alternative_group_is_allowed_and_two_are_not():
    assert broken_rows({"M1", "M4"}, MAINS, 100) == set()
    assert broken_rows({"M1", "M4", "M5"}, MAINS, 100) == {"alt_G1"}
