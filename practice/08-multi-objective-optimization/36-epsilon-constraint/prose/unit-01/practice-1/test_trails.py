import itertools

from trails import Trail, most_visitors

PARK = [
    Trail("Ridge Loop", 900, 10, 40),
    Trail("Marsh Boardwalk", 400, 60, 35),
    Trail("Canyon Spur", 700, 25, 30),
    Trail("Meadow Path", 300, 45, 20),
    Trail("Lake Link", 500, 5, 25),
]
BUDGET = 100


def by_hand(trails, budget, floor):
    """The answer, from every affordable choice listed by hand."""
    best = None
    for k in range(len(trails) + 1):
        for pick in itertools.combinations(trails, k):
            if sum(t.cost for t in pick) <= budget and sum(t.acres for t in pick) >= floor:
                key = sum(t.visitors for t in pick)
                if best is None or key > best[0]:
                    best = (key, tuple(sorted(t.name for t in pick)))
    return None if best is None else best[1]


def visitors(names):
    return sum(t.visitors for t in PARK if t.name in names)


def acres(names):
    return sum(t.acres for t in PARK if t.name in names)


def test_a_pledge_the_busiest_choice_already_meets_changes_nothing():
    busiest = by_hand(PARK, BUDGET, 0)
    got = most_visitors(PARK, BUDGET, acres(busiest) - 5)
    assert got == busiest


def test_a_pledge_that_binds_trades_visitors_for_habitat():
    got = most_visitors(PARK, BUDGET, 100)
    assert got is not None and acres(got) >= 100
    assert visitors(got) == visitors(by_hand(PARK, BUDGET, 100))


def test_at_least_includes_exactly():
    pair = [Trail("North Fork", 800, 30, 50), Trail("South Fork", 200, 50, 50)]
    assert most_visitors(pair, 50, 30) == ("North Fork",)


def test_an_unreachable_pledge_returns_none():
    assert most_visitors(PARK, BUDGET, 500) is None
