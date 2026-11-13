from checker import Limits, Project, broken_rules

# A telecom operator's tower upgrades, not the lessons' portfolio.
PROJECTS = [
    Project("A", 40, 3, "N"),
    Project("B", 30, 2, "N"),
    Project("C", 30, 4, "S"),
    Project("D", 20, 1, "S"),
    Project("E", 70, 2, "W"),
    Project("F", 10, 1, "W"),
]
LIMITS = Limits(budget=100, crew=7, region_cap={"N": 2, "S": 2, "W": 2},
                conflicts=[("C", "E")], needs=[("D", "F")])


def test_a_valid_plan_breaks_nothing_and_an_expensive_one_breaks_the_budget():
    assert broken_rules({"B", "E"}, PROJECTS, LIMITS) == []
    assert broken_rules({"A", "E"}, PROJECTS, LIMITS) == ["budget"]


def test_a_conflicting_pair_is_reported():
    assert broken_rules({"C", "E"}, PROJECTS, LIMITS) == ["conflict_C_E"]


def test_a_need_runs_one_way():
    assert broken_rules({"F"}, PROJECTS, LIMITS) == []
    assert broken_rules({"D"}, PROJECTS, LIMITS) == ["needs_D_F"]


def test_a_region_exactly_at_its_cap_is_fine():
    assert broken_rules({"A", "B"}, PROJECTS, LIMITS) == []


def test_every_broken_rule_is_reported():
    assert broken_rules({"A", "C", "E"}, PROJECTS, LIMITS) == ["budget", "conflict_C_E", "crews"]


def test_a_region_with_no_cap_entry_has_no_cap():
    towers = PROJECTS + [Project("G", 5, 0, "X"), Project("H", 5, 0, "X"), Project("I", 5, 0, "X")]
    assert broken_rules({"G", "H", "I"}, towers, LIMITS) == []
    assert broken_rules({"A", "B", "G", "H", "I"}, towers, Limits(100, 7, {"N": 1, "X": 2})) == [
        "region_N", "region_X"]
