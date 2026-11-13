from plan import Plan, copy_plan


def base() -> Plan:
    return Plan("R-1", "base", {2027: 900, 2028: 950}, {"north": [3, 3, 4], "south": [2, 2, 2]},
                created_by="analyst-a", tags=["draft"])


def test_the_copy_has_its_own_identity_and_the_same_inputs():
    b = base()
    c = copy_plan(b, "R-2", "storm reserve", "analyst-b")
    assert (c.plan_id, c.name, c.created_by) == ("R-2", "storm reserve", "analyst-b")
    assert (c.budget, c.crews, c.tags) == (b.budget, b.crews, b.tags)


def test_a_budget_edit_on_the_copy_leaves_the_parent_alone():
    b = base()
    c = copy_plan(b, "R-2", "storm reserve", "analyst-b")
    c.budget[2028] = 700
    assert b.budget[2028] == 950 and c.budget[2028] == 700


def test_a_crew_edit_inside_a_month_list_leaves_the_parent_alone():
    b = base()
    c = copy_plan(b, "R-2", "storm reserve", "analyst-b")
    c.crews["north"][1] = 0
    assert b.crews["north"] == [3, 3, 4] and c.crews["north"] == [3, 0, 4]


def test_the_copy_points_to_its_parent():
    b = base()
    b.parent_id = "R-0"
    c = copy_plan(b, "R-2", "storm reserve", "analyst-b")
    assert c.parent_id == "R-1" and b.parent_id == "R-0"
