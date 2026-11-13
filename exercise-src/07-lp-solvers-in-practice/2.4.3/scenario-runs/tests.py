import pytest

from scenarios import build, run_scenarios


def test_the_base_and_a_budget_cut_give_their_optima():
    model, rows = build()
    assert run_scenarios(model, rows, [{}, {"budget": 14}]) == [pytest.approx(49), pytest.approx(39)]


def test_a_scenario_changing_two_rows_uses_both():
    model, rows = build()
    assert run_scenarios(model, rows, [{"budget": 14, "staff": 6}]) == [pytest.approx(34)]


def test_each_scenario_starts_from_the_base_data():
    model, rows = build()
    assert run_scenarios(model, rows, [{"budget": 14}, {"staff": 12}]) == [pytest.approx(39), pytest.approx(53)]
    assert rows["budget"].upper_bound == 20 and rows["staff"].upper_bound == 9


def test_an_infeasible_scenario_gives_none_and_the_next_one_still_solves():
    model, rows = build()
    assert run_scenarios(model, rows, [{"budget": 5}, {"budget": 14}]) == [None, pytest.approx(39)]
