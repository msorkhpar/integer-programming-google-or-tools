import pytest

from prices import Unit, price

# An island grid's units, not the lesson's portfolio.
FLEET = {"hydro": Unit(10, 60, 100, 5), "gas": Unit(40, 120, 900, 30), "peaker": Unit(5, 50, 300, 80)}


def run(demand):
    try:
        return price(FLEET, demand)
    except Exception as error:
        raise AssertionError(f"price raised {type(error).__name__}: {error}") from None


def test_the_cheapest_commitment_for_three_demands():
    assert run(30)[0] == pytest.approx(250)
    assert run(150)[0] == pytest.approx(4000)
    assert run(200)[0] == pytest.approx(6800)


def test_a_demand_beyond_hydro_and_gas_starts_the_peaker():
    assert run(220)[0] == pytest.approx(8400)


def test_the_price_is_the_committed_plans_not_the_lp_relaxations():
    assert run(30)[1] == pytest.approx(5)
    assert run(150)[1] == pytest.approx(30)
    assert run(200)[1] == pytest.approx(80)
