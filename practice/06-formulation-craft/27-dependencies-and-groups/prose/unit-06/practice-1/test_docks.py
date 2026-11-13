from ortools.math_opt.python import mathopt

from docks import Vessel, apply_overrides, build, undo_overrides

# A ferry fleet, not the lesson's portfolio.
YEARS = (2027, 2028, 2029, 2030, 2031)
VESSELS = [Vessel("ISLA", YEARS), Vessel("MARA", YEARS), Vessel("NORA", (2028, 2029, 2030)),
           Vessel("ORCA", YEARS)]
OVERRIDES = [("lock", "ISLA", 2029), ("ban", "MARA"), ("by", "NORA", 2029)]


def allowed(plan: set[tuple[str, int]], overrides=OVERRIDES) -> bool:
    """Apply the overrides, then ask whether the model accepts the plan within the bounds left."""
    model, x = build(VESSELS)
    apply_overrides(x, VESSELS, overrides)
    for key, var in x.items():
        value = 1.0 if key in plan else 0.0
        if not var.lower_bound <= value <= var.upper_bound:
            return False
        var.lower_bound = var.upper_bound = value
    result = mathopt.solve(model, mathopt.SolverType.HIGHS)
    return result.termination.reason == mathopt.TerminationReason.OPTIMAL


def test_a_locked_vessel_docks_in_its_year():
    assert allowed({("ISLA", 2029)}) is True
    assert allowed({("ISLA", 2028)}) is False
    assert allowed(set()) is False


def test_a_banned_vessel_does_not_dock():
    assert allowed({("ISLA", 2029), ("ORCA", 2027)}) is True
    assert allowed({("ISLA", 2029), ("MARA", 2030)}) is False


def test_a_deadline_is_met():
    assert allowed({("ISLA", 2029), ("NORA", 2028)}) is True
    assert allowed({("ISLA", 2029), ("NORA", 2030)}) is False


def test_docking_in_the_deadline_year_is_allowed():
    assert allowed({("ISLA", 2029), ("NORA", 2029)}) is True
    assert allowed({("ISLA", 2029), ("ORCA", 2031)}, [("lock", "ISLA", 2029), ("by", "ORCA", 2030)]) is False


def test_undo_restores_every_bound():
    model, x = build(VESSELS)
    x["ORCA", 2031].upper_bound = 0          # set earlier by another rule
    x["ORCA", 2027].lower_bound = 1
    changes = apply_overrides(x, VESSELS, [*OVERRIDES, ("ban", "ORCA")])
    assert x["ORCA", 2027].upper_bound == 0
    undo_overrides(changes)
    assert (x["ORCA", 2031].lower_bound, x["ORCA", 2031].upper_bound) == (0, 0)
    assert (x["ORCA", 2027].lower_bound, x["ORCA", 2027].upper_bound) == (1, 1)
    assert all((v.lower_bound, v.upper_bound) == (0, 1) for (vid, t), v in x.items() if vid != "ORCA")


def test_a_lock_outside_the_vessels_years_keeps_it_out_of_dock():
    overrides = [("lock", "ISLA", 2029), ("lock", "NORA", 2027)]      # NORA may dock only 2028 to 2030
    assert allowed({("ISLA", 2029)}, overrides) is True
    assert allowed({("ISLA", 2029), ("NORA", 2028)}, overrides) is False
