import pytest

from tuning import score, tune

CONFIGS = ["default", "deep-dive", "quick-plans", "no-presolve"]
WORK = {
    # the four training instances
    ("north-1", "default"): 4000.0, ("north-1", "deep-dive"): 2500.0, ("north-1", "quick-plans"): 3600.0, ("north-1", "no-presolve"): 4100.0,
    ("north-2", "default"): 3000.0, ("north-2", "deep-dive"): 2000.0, ("north-2", "quick-plans"): 2900.0, ("north-2", "no-presolve"): 3100.0,
    ("north-3", "default"): 5000.0, ("north-3", "deep-dive"): 5200.0, ("north-3", "quick-plans"): 4500.0, ("north-3", "no-presolve"): 5000.0,
    ("north-4", "default"): 2000.0, ("north-4", "deep-dive"): 2100.0, ("north-4", "quick-plans"): 1900.0, ("north-4", "no-presolve"): 2050.0,
    # held-out instances
    ("south-1", "default"): 3000.0, ("south-1", "deep-dive"): 3300.0, ("south-1", "quick-plans"): 3100.0, ("south-1", "no-presolve"): 3000.0,
    ("south-2", "default"): 6000.0, ("south-2", "deep-dive"): 6500.0, ("south-2", "quick-plans"): 6100.0, ("south-2", "no-presolve"): 6200.0,
    ("tiny-1", "default"): 2.0, ("tiny-1", "deep-dive"): 9.0, ("tiny-1", "quick-plans"): 2.0, ("tiny-1", "no-presolve"): 2.0,
    ("north-5", "default"): 3000.0, ("north-5", "deep-dive"): 3000.0, ("north-5", "quick-plans"): 3000.0, ("north-5", "no-presolve"): 3600.0,
    ("tiny-2", "default"): 9.0, ("tiny-2", "deep-dive"): 9.0, ("tiny-2", "quick-plans"): 9.0, ("tiny-2", "no-presolve"): 1.0,
}
TRAIN = ["north-1", "north-2", "north-3", "north-4"]
TEST = ["south-1", "south-2"]


def test_the_choice_is_made_on_the_training_set_and_scored_on_both():
    chosen, on_train, on_test = tune(WORK, CONFIGS, TRAIN, TEST, shift=100)
    assert chosen == "deep-dive"
    assert on_train == pytest.approx(0.822, abs=0.005)
    assert on_test == pytest.approx(1.091, abs=0.005)


def test_a_score_is_a_shifted_geometric_mean_of_work():
    assert score(WORK, "default", ["north-1", "north-2"], shift=100) == pytest.approx(3465, abs=5)


def test_the_test_instances_never_influence_the_choice():
    heavy = dict(WORK)
    heavy["south-1", "quick-plans"] = 1.0
    heavy["south-2", "quick-plans"] = 1.0
    assert tune(heavy, CONFIGS, TRAIN, TEST, shift=100)[0] == "deep-dive"


def test_ratios_are_to_the_default_not_to_the_best():
    _, on_train, on_test = tune(WORK, CONFIGS, ["north-3"], ["north-1"], shift=100)
    assert on_train == pytest.approx(0.9, abs=1e-3)
    assert on_test == pytest.approx(0.9, abs=1e-3)


def test_a_tie_goes_to_the_earlier_configuration():
    assert tune(WORK, CONFIGS, ["tiny-1"], TEST, shift=100)[0] == "default"


def test_the_shift_keeps_a_tiny_instance_from_deciding():
    assert tune(WORK, ["default", "no-presolve"], ["tiny-2", "north-5"], TEST, shift=100)[0] == "default"
