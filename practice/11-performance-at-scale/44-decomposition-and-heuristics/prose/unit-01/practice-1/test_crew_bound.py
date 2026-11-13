import itertools

import pytest

from crew_bound import crew_bound

HOURS = {2027: 40, 2028: 40, 2029: 40}
BUILDS = {
    "north ring": {"value": {2027: 50, 2028: 44}, "hours": [30, 10], "must": False},
    "harbor spur": {"value": {2027: 22, 2028: 25, 2029: 20}, "hours": [20], "must": False},
    "depot link": {"value": {2028: 30, 2029: 28}, "hours": [15, 15], "must": True},
    "school loop": {"value": {2027: 12, 2029: 15}, "hours": [10], "must": False},
}


def best_plan_value(builds, hours):
    """The best plan that fits every crew row, by trying every plan."""
    names = list(builds)
    best = None
    for combo in itertools.product(*[[None, *builds[n]["value"]] for n in names]):
        if any(t is None and builds[n]["must"] for n, t in zip(names, combo)):
            continue
        used = {y: 0 for y in hours}
        for n, t in zip(names, combo):
            if t is not None:
                for k, h in enumerate(builds[n]["hours"]):
                    used[t + k] = used.get(t + k, 0) + h
        if all(used[y] <= hours.get(y, 0) for y in used):
            value = sum(builds[n]["value"][t] for n, t in zip(names, combo) if t is not None)
            best = value if best is None else max(best, value)
    return best


def test_with_free_crews_every_project_starts_in_its_best_year():
    bound, plan = crew_bound(BUILDS, HOURS, {2027: 0, 2028: 0, 2029: 0, 2030: 0})
    assert plan == {"north ring": 2027, "harbor spur": 2028, "depot link": 2028, "school loop": 2029}
    assert bound == pytest.approx(50 + 25 + 30 + 15)


def test_unused_crew_hours_are_paid_for():
    prices = {2027: 5, 2028: 5, 2029: 5, 2030: 5}
    builds = {k: v for k, v in BUILDS.items() if not v["must"]}
    bound, plan = crew_bound(builds, HOURS, prices)
    assert plan == {}
    assert bound == pytest.approx(5 * 120)


def test_a_project_worth_less_than_its_crews_is_not_started():
    prices = {2027: 1.0, 2028: 1.0, 2029: 1.0, 2030: 1.0}
    bound, plan = crew_bound(BUILDS, HOURS, prices)
    # north ring 50 - 40 = 10; harbor spur 25 - 20 = 5; depot link 30 - 30 = 0; school loop 15 - 10 = 5
    assert "north ring" in plan and "harbor spur" in plan and "school loop" in plan
    assert bound == pytest.approx(120 + 10 + 5 + 0 + 5)
    priced_out = {"lonely spur": {"value": {2027: 9}, "hours": [10], "must": False}}
    assert crew_bound(priced_out, {2027: 40}, {2027: 1.0}) == (pytest.approx(40.0), {})


def test_a_must_do_starts_even_at_a_loss():
    prices = {2027: 2.0, 2028: 2.0, 2029: 1.5, 2030: 1.5}
    builds = {"depot link": BUILDS["depot link"]}
    bound, plan = crew_bound(builds, HOURS, prices)
    # 2028: 30 - 15*2 - 15*1.5 = -22.5; 2029: 28 - 15*1.5 - 15*1.5 = -17
    assert plan == {"depot link": 2029}
    assert bound == pytest.approx(2 * 40 + 2 * 40 + 1.5 * 40 - 17)


def test_hours_are_priced_in_every_year_of_work():
    prices = {2027: 0.0, 2028: 3.0, 2029: 0.0, 2030: 0.0}
    builds = {"north ring": BUILDS["north ring"]}
    bound, plan = crew_bound(builds, HOURS, prices)
    # 2027: 50 - 10*3 = 20; 2028: 44 - 30*3 = -46
    assert plan == {"north ring": 2027}
    assert bound == pytest.approx(3 * 40 + 20)


def test_the_bound_is_never_below_the_best_plan():
    hours = {2027: 35, 2028: 30, 2029: 25, 2030: 0}
    best = best_plan_value(BUILDS, hours)
    for prices in ({2027: 0.2, 2028: 0.4, 2029: 0.1, 2030: 0.0},
                   {2027: 0.9, 2028: 0.3, 2029: 0.6, 2030: 0.6},
                   {2027: 0.0, 2028: 1.2, 2029: 0.0, 2030: 0.5}):
        bound, _ = crew_bound(BUILDS, hours, prices)
        assert bound >= best - 1e-9, prices
