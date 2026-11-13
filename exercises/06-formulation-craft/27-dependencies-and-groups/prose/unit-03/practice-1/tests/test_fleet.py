from ortools.math_opt.python import mathopt

from fleet import Bus, build

# An agency's buses, not the lesson's portfolio.
BUSES = [Bus("B101", 4), Bus("B102", 9), Bus("B103", 15), Bus("B104", 17), Bus("B105", 21)]
CHARGERS = 2
MAX_AGE = 15

GOOD = {"B101": "keep", "B102": "electric", "B103": "refurbish", "B104": "electric", "B105": "diesel"}


def allowed(plan: dict[str, str | set[str]]) -> bool:
    """Fix every option variable to the plan (a bus may be given a set of options) and solve."""
    model, y = build(BUSES, CHARGERS, MAX_AGE)
    for (bid, option), var in y.items():
        chosen = plan.get(bid, set())
        value = 1.0 if option == chosen or (isinstance(chosen, set) and option in chosen) else 0.0
        if value > var.upper_bound:
            return False
        var.lower_bound = var.upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_each_bus_gets_one_option():
    assert allowed(GOOD) is True
    assert allowed({**GOOD, "B101": {"keep", "refurbish"}}) is False


def test_electric_buses_fit_the_chargers():
    assert allowed({**GOOD, "B104": "diesel", "B101": "electric"}) is True
    assert allowed({**GOOD, "B101": "electric"}) is False


def test_an_old_bus_is_not_kept():
    assert allowed({**GOOD, "B104": "refurbish"}) is True
    assert allowed({**GOOD, "B104": "keep"}) is False


def test_every_bus_gets_an_option():
    assert allowed(GOOD) is True
    assert allowed({bid: o for bid, o in GOOD.items() if bid != "B102"}) is False


def test_a_bus_at_the_age_limit_may_be_kept():
    assert allowed({**GOOD, "B103": "keep"}) is True
    assert allowed({**GOOD, "B105": "keep"}) is False
