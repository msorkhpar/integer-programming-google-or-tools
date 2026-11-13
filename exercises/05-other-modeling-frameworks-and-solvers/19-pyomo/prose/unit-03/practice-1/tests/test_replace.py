import pytest

from replace import Asset, plan

# Two fleets of substation transformers, not the lesson's portfolio. Costs in $k, ratings in MVA.
TOWN = {"T1": Asset(120, 400, 30, 60), "T2": Asset(90, 350, 25, 50),
        "T3": Asset(150, 500, 40, 75), "T4": Asset(60, 260, 20, 35)}
CITY = {"S1": Asset(200, 900, 45, 90), "S2": Asset(300, 2500, 60, 140), "S3": Asset(80, 300, 20, 40)}


def run(assets, demand):
    try:
        return plan(assets, demand)
    except Exception as error:
        raise AssertionError(f"plan raised {type(error).__name__}: {error}") from None


def carried(assets, choice):
    return sum(a.new if choice[i] == "replace" else a.repaired for i, a in assets.items())


def costed(assets, choice):
    return sum(a.replace if choice[i] == "replace" else a.repair for i, a in assets.items())


def test_one_replacement_is_enough_for_a_moderate_load():
    cost, choice = run(TOWN, 150)
    assert cost == pytest.approx(770)
    assert choice == {"T1": "repair", "T2": "repair", "T3": "replace", "T4": "repair"}


def test_a_heavy_load_replaces_three_and_still_carries_it():
    cost, choice = run(TOWN, 200)
    assert cost == pytest.approx(1310)
    assert carried(TOWN, choice) >= 200 and costed(TOWN, choice) == pytest.approx(cost)


def test_large_replacement_costs_do_not_leak_into_a_repair_plan():
    cost, choice = run(CITY, 100)
    assert cost == pytest.approx(580)
    assert set(choice.values()) == {"repair"}
    cost, choice = run(CITY, 200)
    assert cost == pytest.approx(2780) and choice["S2"] == "replace"
