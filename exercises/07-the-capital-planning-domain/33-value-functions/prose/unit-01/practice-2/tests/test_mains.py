import pytest

from mains import Main, benefit

# beta 2 and eta 10, so breaks between ages a and a + h are (2ah + h^2) / 100.
ELM = Main("Elm St", 20, 2.0, 10.0, 50, 6.0)       # 300 household-hours per break


def renew(depth, start, duration=0):
    return benefit(ELM, depth, start, duration, 2030, 10)


def test_a_replacement_avoids_the_breaks_worked_out_by_hand():
    got = renew(1.0, 2030)                          # 5.0 breaks as it is, 1.0 as new
    assert got["breaks"] == pytest.approx(4.0)
    assert got["household_hours"] == pytest.approx(1_200)


def test_a_relining_takes_away_part_of_the_age():
    got = renew(0.5, 2030)                          # 5.0 breaks at age 20, 3.0 at age 10
    assert got["breaks"] == pytest.approx(2.0)
    assert got["household_hours"] == pytest.approx(600)


def test_a_later_start_counts_fewer_years_on_an_older_main():
    got = renew(1.0, 2033)                          # age 23, 7 years left: 3.71 - 0.49
    assert got["breaks"] == pytest.approx(3.22)


def test_benefits_start_when_the_work_is_finished():
    got = renew(1.0, 2030, duration=2)              # in service 2032 at age 22, 8 years left
    assert got["breaks"] == pytest.approx(3.52)


def test_the_main_keeps_aging_while_it_waits_and_while_it_is_worked_on():
    got = renew(0.5, 2031, duration=1)              # in service 2032 at age 22 -> 11; 8 years left
    assert got["breaks"] == pytest.approx(1.76)


def test_work_finished_after_the_window_avoids_nothing():
    assert renew(1.0, 2030)["breaks"] > 0
    assert renew(1.0, 2038, duration=3) == {"breaks": 0.0, "household_hours": 0.0}
