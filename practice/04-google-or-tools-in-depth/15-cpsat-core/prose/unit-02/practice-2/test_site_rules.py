from ortools.sat.python import cp_model

from site_rules import add_site_rules, site_variables

MIN_NIGHT, FORKLIFTS_BOTH = 4, 3      # a test warehouse's numbers, not the lesson's


def allowed(**fixed: int) -> bool:
    """Fix some of the day's decisions (unnamed Booleans are 0, unnamed counts are free) and ask CP-SAT."""
    model = cp_model.CpModel()
    v = site_variables(model)
    add_site_rules(model, v, MIN_NIGHT, FORKLIFTS_BOTH)
    for name in ("night", "freezer", "dock_a", "dock_b"):
        model.add(v[name] == fixed.get(name, 0))
    for name in ("night_staff", "frozen_orders", "forklifts"):
        if name in fixed:
            model.add(v[name] == fixed[name])
    return cp_model.CpSolver().solve(model) == cp_model.OPTIMAL


def test_a_night_shift_has_its_minimum_crew():
    assert allowed(night=1, night_staff=5) is True
    assert allowed(night=1, night_staff=2) is False


def test_a_closed_freezer_takes_no_frozen_orders():
    assert allowed(freezer=0, frozen_orders=0) is True
    assert allowed(freezer=0, frozen_orders=120) is False


def test_two_open_docks_need_their_forklifts():
    assert allowed(dock_a=1, dock_b=1, forklifts=3) is True
    assert allowed(dock_a=1, dock_b=1, forklifts=2) is False


def test_one_open_dock_needs_no_extra_forklifts():
    assert allowed(dock_a=1, forklifts=1) is True
    assert allowed(dock_b=1, forklifts=1) is True
    assert allowed(dock_a=1, dock_b=1, forklifts=1) is False


def test_no_night_shift_means_no_night_staff():
    assert allowed(night=0, night_staff=0) is True
    assert allowed(night=0, night_staff=3) is False


def test_an_open_freezer_takes_frozen_orders():
    assert allowed(freezer=1, frozen_orders=120) is True
    assert allowed(freezer=0, frozen_orders=1) is False
