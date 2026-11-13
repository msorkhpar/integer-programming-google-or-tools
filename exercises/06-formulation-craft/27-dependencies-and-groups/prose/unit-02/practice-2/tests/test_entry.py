from entry import Project, entry_cost, implied_required

# A water utility's projects, not the lesson's portfolio:
# TOWER needs MAIN and PUMP; PUMP needs MAIN; MAIN needs PLANT. METER needs nothing.
PROJECTS = {
    "PLANT": Project(900),
    "MAIN": Project(400, ("PLANT",)),
    "PUMP": Project(150, ("MAIN",)),
    "TOWER": Project(300, ("MAIN", "PUMP")),
    "METER": Project(40),
    "VALVE": Project(60, ("METER",)),
}


def test_a_project_with_no_prerequisites_costs_itself():
    assert entry_cost(PROJECTS, "METER") == 40
    assert entry_cost(PROJECTS, "PLANT") == 900


def test_a_prerequisite_is_paid_for():
    assert entry_cost(PROJECTS, "VALVE") == 100
    assert entry_cost(PROJECTS, "MAIN") == 1300


def test_a_required_project_makes_its_prerequisites_required():
    assert implied_required(PROJECTS, {"VALVE"}) == {"METER"}
    assert implied_required(PROJECTS, {"MAIN", "PLANT"}) == set()


def test_prerequisites_of_prerequisites_count():
    assert entry_cost(PROJECTS, "PUMP") == 1450
    assert implied_required(PROJECTS, {"PUMP", "METER"}) == {"MAIN", "PLANT"}


def test_a_shared_prerequisite_is_paid_once():
    assert entry_cost(PROJECTS, "TOWER") == 1750
