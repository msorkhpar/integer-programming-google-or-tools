from answers import usable


def test_a_confirmed_lp_bound_is_used():
    accepted, value = usable("bound", {"status": "Optimal", "objective": 812_400.0}, {"objective": 812_400.0})
    assert accepted is True and value == 812_400.0
    assert usable("bound", {"status": "Optimal", "objective": 812_400.0}, {"objective": 820_000.0}) == (False, "not confirmed")


def test_the_plan_of_record_never_comes_from_the_gpu():
    assert usable("plan", {"status": "Optimal", "objective": 9.0, "x": [1, 0]},
                  {"objective": 9.0, "feasible": True, "integral": True}) == (False, "the plan of record runs on the CPU")


def test_a_checked_start_is_used_whatever_its_status_label():
    assert usable("start", {"status": "FeasibleFound", "x": [1, 0, 1]}, {"feasible": True, "integral": True}) == (True, [1, 0, 1])
    assert usable("start", {"status": "FeasibleFound", "x": [1, 1, 1]}, {"feasible": False, "integral": True}) == (False, "fails the check")


def test_a_bound_is_reported_at_the_larger_of_the_two_values():
    accepted, value = usable("bound", {"status": "Optimal", "objective": 812_399.9995}, {"objective": 812_400.0})
    assert accepted is True and value == 812_400.0


def test_confirmation_is_relative_to_the_objective():
    assert usable("bound", {"status": "Optimal", "objective": 2_000_000_001.0}, {"objective": 2_000_000_000.0})[0] is True
    assert usable("bound", {"status": "Optimal", "objective": 2_000_010_000.0}, {"objective": 2_000_000_000.0}) == (False, "not confirmed")


def test_a_bound_whose_status_is_not_optimal_is_not_used():
    assert usable("bound", {"status": "Unknown", "objective": 812_400.0}, {"objective": 812_400.0}) == (False, "not optimal")
