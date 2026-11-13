import pytest

from split import Terminal, split

PORT = [Terminal("north", 1.2, 2, 400), Terminal("south", 0.9, 1, 300), Terminal("east", 0.7, 4, 800)]


def test_the_best_split_its_value_and_its_full_rows():
    status, value, amounts, full = split(PORT, 600)
    assert status == "OPTIMAL"
    assert value == pytest.approx(580)
    assert amounts == {"north": pytest.approx(200), "south": pytest.approx(300), "east": pytest.approx(100)}
    assert full == {"budget", "labour_north", "labour_south"}


def test_amounts_are_not_rounded_to_whole_thousands():
    status, value, amounts, _ = split(PORT, 600.5)
    assert status == "OPTIMAL"
    assert amounts["east"] == pytest.approx(100.5)
    assert value == pytest.approx(580.35)


def test_floors_above_the_budget_give_infeasible_with_no_answer():
    floors = [Terminal("north", 1.2, 2, 400, 200), Terminal("south", 0.9, 1, 300, 300),
              Terminal("east", 0.7, 4, 800, 200)]
    assert split(floors, 600) == ("INFEASIBLE", None, None, None)


def test_a_floor_is_a_least_amount_that_the_split_must_reach():
    port = [PORT[0], PORT[1], Terminal("east", 0.7, 4, 800, 150)]
    status, value, amounts, _ = split(port, 600)
    assert status == "OPTIMAL"
    assert amounts["east"] == pytest.approx(150)
    assert value == pytest.approx(570)


def test_a_split_resting_on_its_floor_lists_the_floor_as_full():
    port = [PORT[0], PORT[1], Terminal("east", 0.7, 4, 800, 150)]
    assert split(port, 600)[3] == {"budget", "labour_north", "floor_east"}


def test_no_terminal_gets_a_negative_amount():
    open_berths = [Terminal("north", 1.2, 1, 1000), Terminal("south", 0.5, 1, 1000)]
    status, value, amounts, _ = split(open_berths, 500)
    assert status == "OPTIMAL"
    assert min(amounts.values()) >= -1e-9
    assert value == pytest.approx(600)
