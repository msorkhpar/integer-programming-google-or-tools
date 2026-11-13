from rows import Project, rows_for

# A gas utility's fleets, not the lesson's portfolio.
YEARS = [2027, 2028, 2029, 2030]


def test_a_lone_project_has_its_once_budget_and_crew_rows():
    projects = [Project("M1", "mains", 2028, 2028, 2)]
    assert rows_for("M1", projects, YEARS) == {
        "once_M1", "budget_2028", "budget_2029", "crew_mains_2028", "crew_mains_2029"}


def test_must_do_and_alternative_rows():
    projects = [Project("R1", "regulators", 2027, 2027, 1, must_do=True),
                Project("V1", "valves", 2029, 2029, 1, alt_group="G1"),
                Project("V2", "valves", 2029, 2029, 1, alt_group="G1")]
    assert rows_for("R1", projects, YEARS) == {"must_R1", "budget_2027", "crew_regulators_2027"}
    assert rows_for("V2", projects, YEARS) == {"once_V2", "alt_G1", "budget_2029", "crew_valves_2029"}


def test_a_parent_sits_in_its_childrens_rows():
    projects = [Project("P", "mains", 2027, 2027, 1), Project("C", "mains", 2028, 2029, 1, parent="P", lag=1)]
    assert rows_for("P", projects, YEARS) == {
        "once_P", "after_C_2028", "after_C_2029", "budget_2027", "crew_mains_2027"}
    assert rows_for("C", projects, YEARS) == {
        "once_C", "after_C_2028", "after_C_2029", "budget_2028", "budget_2029", "crew_mains_2028", "crew_mains_2029"}


def test_a_parent_is_absent_from_rows_its_starts_cannot_reach():
    projects = [Project("P", "mains", 2028, 2028, 1), Project("C", "mains", 2028, 2030, 1, parent="P", lag=1)]
    assert rows_for("P", projects, YEARS) == {"once_P", "after_C_2029", "after_C_2030", "budget_2028", "crew_mains_2028"}


def test_budget_years_cover_every_start_and_year_of_work():
    projects = [Project("M1", "mains", 2027, 2029, 2)]
    assert rows_for("M1", projects, YEARS) == {
        "once_M1", "budget_2027", "budget_2028", "budget_2029", "budget_2030",
        "crew_mains_2027", "crew_mains_2028", "crew_mains_2029", "crew_mains_2030"}
