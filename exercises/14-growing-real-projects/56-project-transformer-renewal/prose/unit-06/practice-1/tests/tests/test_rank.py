from renewal.fleet import Transformer
from renewal.rank import worst_first


def unit(tid, condition, cost):
    return Transformer(tid, "S0001", "north", "small", 50, cost, 1000, condition, 0.05)


def test_worst_first_takes_the_worst_units_until_one_does_not_fit():
    fleet = [unit("A", 90, 400), unit("B", 80, 400), unit("C", 70, 300), unit("D", 60, 100)]
    assert worst_first(fleet, 1000) == ["A", "B"]
