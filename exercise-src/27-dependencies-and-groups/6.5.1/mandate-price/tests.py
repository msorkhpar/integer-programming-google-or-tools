import pytest

from parks import Project, best_value, mandate_costs

# Two court-ordered repairs that fill the budget, one cheap inspection fix the plan wants anyway,
# and discretionary work. Not the lesson's portfolio.
PROJECTS = [
    Project("FENCE", 5, 1, mandated=True),
    Project("STEPS", 5, 1, mandated=True),
    Project("LIGHTS", 1, 10, mandated=True),
    Project("POOL", 10, 20),
    Project("TRAIL", 5, 3),
    Project("BENCH", 5, 3),
]
BUDGET = 11


def test_the_best_value_keeps_every_mandate():
    assert best_value(PROJECTS, BUDGET, {"FENCE", "STEPS", "LIGHTS"}) == pytest.approx(12)
    assert best_value(PROJECTS, BUDGET, set()) == pytest.approx(30)


def test_each_mandate_is_priced():
    costs = mandate_costs(PROJECTS, BUDGET)
    assert costs["FENCE"] == pytest.approx(2)
    assert costs["STEPS"] == pytest.approx(2)


def test_a_mandate_the_plan_meets_anyway_costs_nothing():
    assert mandate_costs(PROJECTS, BUDGET)["LIGHTS"] == pytest.approx(0)


def test_the_joint_cost_is_not_the_sum():
    projects = [Project("A", 4, 2, mandated=True), Project("B", 4, 2, mandated=True),
                Project("BIG", 8, 9), Project("C", 4, 3)]
    costs = mandate_costs(projects, 8)
    assert costs["A"] == pytest.approx(1)
    assert costs["all"] == pytest.approx(5)
    assert mandate_costs(PROJECTS, BUDGET)["all"] == pytest.approx(18)
