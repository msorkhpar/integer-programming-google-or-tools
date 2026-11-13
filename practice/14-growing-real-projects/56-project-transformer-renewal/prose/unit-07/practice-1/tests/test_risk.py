import math

from renewal.fleet import Transformer, generate_fleet
from renewal.request import Request
from renewal.risk import pof_next, risk_removed


def old_unit(age=60, cof=5000):
    return Transformer("A", "S0001", "north", "medium", age, 1000, cof, 80, 0.0)


def test_the_curve_reproduces_the_fleet_pof_column():
    for t in generate_fleet(50):
        assert abs(pof_next(t.age, t.kind) - t.pof) < 1e-5


def test_a_later_replacement_removes_less_risk():
    request = Request(budget=0, years=10, window=10)
    early, late = risk_removed(old_unit(), 2027, request), risk_removed(old_unit(), 2030, request)
    assert early > late > 0


def test_risk_removed_counts_the_years_after_the_replacement_discounted():
    request = Request(budget=0, years=3, window=3, rate=0.05)
    def pof(age):                       # the medium kind's curve: beta 3.6, eta 60 years
        return 1 - math.exp((age / 60) ** 3.6 - ((age + 1) / 60) ** 3.6)
    by_hand = (pof(62) - pof(0)) * 5000 / 1.05 ** 2
    assert abs(risk_removed(old_unit(), 2029, request) - by_hand) < 1e-9
