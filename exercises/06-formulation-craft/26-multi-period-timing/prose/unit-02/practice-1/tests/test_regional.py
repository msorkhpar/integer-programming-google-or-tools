import pytest
from ortools.math_opt.python import mathopt

from regional import Project, spend_by_region_year, start_variables

YEARS = [2027, 2028, 2029, 2030]
BACKBONE = [
    Project("F1", "Hill", (120, 480), (2027, 2028)),
    Project("F2", "Hill", (90,), (2028, 2029, 2030)),
    Project("F3", "Lake", (200, 50, 250), (2027, 2028)),
    Project("F4", "Moor", (60, 60), (2028, 2029)),
]


def spend_of(schedule: dict[str, int], projects=BACKBONE) -> dict:
    """Evaluate every (region, year) expression for a schedule {pid: start year}."""
    model = mathopt.Model()
    x = start_variables(model, projects)
    spend = spend_by_region_year(projects, x, YEARS)
    values = {var: 1.0 if schedule.get(pid) == t else 0.0 for (pid, t), var in x.items()}
    return {key: mathopt.evaluate_expression(expr, values) for key, expr in spend.items()}


def test_a_one_region_plan_spends_its_whole_cost():
    hill = [p for p in BACKBONE if p.region == "Hill"]
    spend = spend_of({"F1": 2027, "F2": 2029}, hill)
    assert sum(spend.values()) == pytest.approx(120 + 480 + 90)


def test_the_start_year_carries_only_the_first_year_of_work():
    spend = spend_of({"F1": 2028})
    assert spend["Hill", 2028] == pytest.approx(120)


def test_work_begins_in_the_start_year():
    spend = spend_of({"F2": 2028})
    assert spend["Hill", 2028] == pytest.approx(90)
    assert spend["Hill", 2029] == pytest.approx(0)


def test_an_uneven_profile_keeps_its_shape():
    spend = spend_of({"F3": 2027})
    assert [spend["Lake", y] for y in (2027, 2028, 2029)] == pytest.approx([200, 50, 250])


def test_regions_are_kept_apart():
    spend = spend_of({"F1": 2027, "F4": 2028})
    assert spend["Hill", 2028] == pytest.approx(480)
    assert spend["Moor", 2028] == pytest.approx(60)
    assert spend["Lake", 2028] == pytest.approx(0)


def test_the_last_year_of_the_plan_counts():
    spend = spend_of({"F2": 2030})
    assert spend["Hill", 2030] == pytest.approx(90)
