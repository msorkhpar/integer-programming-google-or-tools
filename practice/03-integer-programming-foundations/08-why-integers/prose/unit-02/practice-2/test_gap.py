import pytest

from gap import Project, integrality_gap

YARDS = [Project("A", 60, 66), Project("B", 50, 60), Project("C", 40, 36)]
LINKED = [Project("P", 50, 40), Project("Q", 40, 64, parent="P"), Project("R", 30, 30)]


def test_the_bound_comes_from_the_relaxation_and_the_optimum_from_the_milp():
    lp_bound, optimum, _ = integrality_gap(YARDS, 100)
    assert lp_bound == pytest.approx(115)
    assert optimum == pytest.approx(102)


def test_the_gap_is_a_share_of_the_best_plans_value():
    assert integrality_gap(YARDS, 100)[2] == pytest.approx(13 / 102)


def test_the_parent_row_holds_the_child_to_its_parents_share():
    lp_bound, optimum, gap = integrality_gap(LINKED, 100)
    assert lp_bound == pytest.approx(114)
    assert optimum == pytest.approx(104)
    assert gap == pytest.approx(10 / 104)
