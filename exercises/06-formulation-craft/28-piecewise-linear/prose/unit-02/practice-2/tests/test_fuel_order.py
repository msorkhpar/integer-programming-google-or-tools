from ortools.math_opt.python import mathopt

from fuel_order import build

# A school district's diesel, not the lesson's credit line. Rates: 1.50, 1.10, 0.80 $ per litre.
XS, YS = (0, 20_000, 50_000, 80_000), (0, 30_000, 63_000, 87_000)


def allowed(volume: float, bill: float, audit: int, xs=XS, ys=YS, audit_above=30_000) -> bool:
    """Fix the order, its bill and the audit, and ask whether the model accepts them."""
    model, v, b, a = build(xs, ys, audit_above)
    v.lower_bound = v.upper_bound = volume
    b.lower_bound = b.upper_bound = bill
    a.lower_bound = a.upper_bound = audit
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_the_bill_follows_the_price_curve():
    assert allowed(10_000, 15_000, 0) is True
    assert allowed(60_000, 71_000, 1) is True               # 63,000 + 0.80 x 10,000
    assert allowed(10_000, 10_875, 0) is False              # the straight line from 0 to 80,000 litres
    assert allowed(60_000, 60_000, 1) is False


def test_a_large_order_needs_an_audit():
    assert allowed(35_000, 46_500, 1) is True               # 30,000 + 1.10 x 15,000
    assert allowed(35_000, 46_500, 0) is False
    assert allowed(70_000, 79_000, 0) is False
    assert allowed(15_000, 22_500, 0, audit_above=10_000) is False      # another audit volume


def test_an_order_below_the_audit_volume_needs_no_audit():
    assert allowed(25_000, 35_500, 0) is True               # 30,000 + 1.10 x 5,000
    assert allowed(25_000, 35_500, 1) is True
    assert allowed(25_000, 30_000, 0) is False


def test_an_order_of_exactly_the_audit_volume_needs_no_audit():
    assert allowed(30_000, 41_000, 0) is True
    assert allowed(30_001, 41_001.1, 0) is False
