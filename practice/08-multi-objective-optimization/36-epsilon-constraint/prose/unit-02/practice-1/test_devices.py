import itertools

import pytest

from devices import Device, augmented_choice

WARD = [
    Device("Ventilator", 120, 4, 60),
    Device("Monitor", 80, 7, 30),
    Device("Infusion Pump", 60, 3, 25),
    Device("Defibrillator", 40, 9, 20),
    Device("Bed Lift", 100, 2, 45),
]


def by_hand(devices, budget, floor):
    """Most beds, then most safety, over every affordable choice that reaches the floor."""
    best = None
    for k in range(len(devices) + 1):
        for chosen in itertools.combinations(devices, k):
            if sum(d.cost for d in chosen) <= budget and sum(d.safety for d in chosen) >= floor:
                key = (sum(d.beds for d in chosen), sum(d.safety for d in chosen))
                if best is None or key > best[0]:
                    best = (key, tuple(sorted(d.name for d in chosen)))
    return best


def test_the_best_choice_and_its_slack_are_returned():
    (beds, safety), names = by_hand(WARD, 100, 12)
    got = augmented_choice(WARD, 100, 12, span=20)
    assert got[0] == names
    assert got[1] == pytest.approx(safety - 12, abs=1e-6)


def test_of_two_choices_with_equal_beds_the_safer_one_wins():
    ward = WARD + [Device("Alarm Panel", 0, 6, 5)]
    (_, safety), names = by_hand(ward, 105, 10)
    got = augmented_choice(ward, 105, 10, span=30)
    assert "Alarm Panel" in names
    assert got[0] == names


def test_no_beds_are_given_up_for_safety_above_the_floor():
    pair = [Device("Scanner", 10, 2, 50), Device("Sterilizer", 9, 20, 50)]
    got = augmented_choice(pair, 50, 0, span=20)
    assert got[0] == ("Scanner",)


def test_an_unreachable_floor_returns_none():
    assert augmented_choice(WARD, 100, 200, span=20) is None
