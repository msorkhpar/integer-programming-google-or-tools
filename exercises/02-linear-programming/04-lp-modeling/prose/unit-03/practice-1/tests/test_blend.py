import pytest

from blend import Pit, mix

PITS = [Pit("A", 12, 4, 900), Pit("B", 9, 9, 900), Pit("C", 7, 14, 900)]


def average_fines(pits, tons_by_pit):
    return sum(p.fines * tons_by_pit[p.name] for p in pits) / sum(tons_by_pit.values())


def test_the_cheapest_blend_meets_the_average_and_the_tonnage():
    status, cost, tons = mix(PITS, 1000, 6, 10)
    assert status == "OPTIMAL"
    assert cost == pytest.approx(8600)
    assert sum(tons.values()) == pytest.approx(1000)
    assert average_fines(PITS, tons) == pytest.approx(10)
    assert tons == {"A": pytest.approx(0, abs=1e-6), "B": pytest.approx(800), "C": pytest.approx(200)}


def test_the_lower_limit_on_the_average_is_kept_too():
    pits = [Pit("D", 5, 2, 800), Pit("E", 11, 10, 600)]
    status, cost, tons = mix(pits, 500, 6, 12)
    assert status == "OPTIMAL"
    assert average_fines(pits, tons) >= 6 - 1e-6
    assert cost == pytest.approx(4000)


def test_no_pit_supplies_more_than_it_has():
    pits = [Pit("A", 12, 4, 900), Pit("B", 9, 9, 900), Pit("C", 7, 14, 100)]
    status, cost, tons = mix(pits, 1000, 6, 10)
    assert status == "OPTIMAL"
    assert tons["C"] <= 100 + 1e-6
    assert cost == pytest.approx(8800)


def test_a_target_no_blend_can_reach_gives_infeasible_with_no_answer():
    assert mix([Pit("B", 9, 9, 900), Pit("C", 7, 14, 900)], 1000, 6, 8) == ("INFEASIBLE", None, None)
