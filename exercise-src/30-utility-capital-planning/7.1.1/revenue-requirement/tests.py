import pytest

from rates import revenue_requirement

# A small water utility's additions, in $k. Not the lesson's numbers.
YEARS = [2027, 2028, 2029, 2030, 2031, 2032]


def test_one_addition_in_its_first_years():
    got = revenue_requirement({2027: 1_000}, 4, 0.10, {}, [2027, 2028, 2029])
    assert got == pytest.approx({2027: 325, 2028: 300, 2029: 275})


def test_two_additions_add_up():
    got = revenue_requirement({2027: 1_000, 2028: 600}, 4, 0.10, {}, [2028, 2029])
    assert got == pytest.approx({2028: 495, 2029: 455})


def test_a_fully_depreciated_addition_drops_out():
    got = revenue_requirement({2027: 1_000}, 4, 0.10, {}, YEARS)
    assert got == pytest.approx({2027: 325, 2028: 300, 2029: 275, 2030: 250, 2031: 0, 2032: 0})


def test_an_addition_earns_nothing_before_service():
    got = revenue_requirement({2029: 800}, 4, 0.05, {}, [2027, 2028, 2029, 2030])
    assert got == pytest.approx({2027: 0, 2028: 0, 2029: 230, 2030: 220})


def test_om_earns_no_return():
    assert revenue_requirement({}, 4, 0.10, {2027: 50, 2028: 70}, [2027, 2028, 2029]) == pytest.approx(
        {2027: 50, 2028: 70, 2029: 0})
    assert revenue_requirement({2027: 1_000}, 4, 0.10, {2027: 50}, [2027]) == pytest.approx({2027: 375})
