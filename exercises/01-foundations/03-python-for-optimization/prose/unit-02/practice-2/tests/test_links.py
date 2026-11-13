from links import Project, link_problems

# Substation upgrades unlike the lesson's portfolio. U1 and U3 are alternatives (group "bus");
# U2 needs U1, U4 needs U3, and U4 and U5 are alternatives (group "relay").
YARD = [
    Project("U1", group="bus"),
    Project("U2", parent="U1"),
    Project("U3", group="bus"),
    Project("U4", parent="U3", group="relay"),
    Project("U5", group="relay"),
]


def test_a_consistent_list_has_no_problems():
    assert link_problems(YARD) == []


def test_a_parent_nobody_has_is_reported():
    assert link_problems(YARD + [Project("U6", parent="U9", group="relay")]) == ["unknown-parent:U6"]


def test_a_child_in_its_parents_group_is_reported():
    assert link_problems(YARD + [Project("U6", parent="U5", group="relay")]) == ["blocked-child:U6"]


def test_a_parent_listed_after_its_child_is_known():
    later = [Project("U7", parent="U8", group="relay"), Project("U8", group="bus")]
    assert link_problems(later) == []


def test_three_copies_of_an_id_are_one_problem():
    copies = YARD + [Project("U5", group="relay"), Project("U5", group="relay")]
    assert link_problems(copies) == ["duplicate:U5"]


def test_a_child_and_parent_with_no_group_are_fine():
    plain = [Project("V1"), Project("V2", parent="V1")]
    assert link_problems(plain) == []


def test_a_project_that_is_its_own_parent_is_reported():
    assert sorted(link_problems(YARD + [Project("U6", parent="U6")])) == ["self-parent:U6"]
