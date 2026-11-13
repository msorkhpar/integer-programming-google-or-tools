from shrink import shrink

# Each lift: (days of crane work, first day allowed, day it must end by), in a 20-day month.
LIFTS = {
    "breaker A": (6, 0, 8), "breaker B": (5, 2, 9), "transformer": (9, 0, 20),
    "bus section": (4, 12, 18), "reactor": (5, 11, 20), "spare": (2, 0, 20),
}


def fits(names):
    """Can one crane do every lift in its window? Earliest deadline first is exact for one crane
    when every lift may start at its first allowed day (no lift may wait for a later release here)."""
    jobs = sorted((LIFTS[n][2], LIFTS[n][1], LIFTS[n][0]) for n in names)
    for order in _orders(jobs):
        day, ok = 0, True
        for deadline, release, days in order:
            day = max(day, release) + days
            ok = ok and day <= deadline
        if ok:
            return True
    return False


def _orders(jobs):
    import itertools
    return itertools.permutations(jobs)


def test_a_conflict_of_two_comes_back_whole():
    assert fits(["breaker A", "breaker B"]) is False
    assert shrink(["breaker A", "breaker B"], fits) == ["breaker A", "breaker B"]


def test_the_core_still_cannot_be_booked():
    names = ["spare", "transformer", "bus section", "reactor", "breaker A"]
    assert fits(names) is False
    core = shrink(names, fits)
    assert core and fits(core) is False
    assert core == [n for n in names if n in core]


def test_no_lift_of_the_core_can_be_spared():
    names = list(LIFTS)
    core = shrink(names, fits)
    assert core and fits(core) is False
    for lift in core:
        assert fits([k for k in core if k != lift]) is True, lift
