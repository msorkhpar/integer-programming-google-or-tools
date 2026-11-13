from verdict import verdict

RUN = {"status": "OPTIMAL", "objective": 118.0, "plan": {"S1": "T2", "S2": "T1", "S3": "T2", "S4": "T3"}}


def test_identical_runs_a_tie_and_a_worse_run():
    assert verdict(RUN, dict(RUN)) == "same"
    other = {**RUN, "plan": {"S1": "T1", "S2": "T2", "S3": "T2", "S4": "T3"}}
    assert verdict(RUN, other) == "tie"
    assert verdict(RUN, {**RUN, "objective": 113.0}) == "different"


def test_float_noise_in_the_objective_is_not_a_difference():
    assert verdict(RUN, {**RUN, "objective": 118.0000000004}, tol=1e-6) == "same"
    assert verdict(RUN, {**RUN, "objective": 118.01}, tol=1e-6) == "different"


def test_a_plan_is_a_set_of_assignments_not_a_sequence():
    shuffled = {**RUN, "plan": {"S4": "T3", "S2": "T1", "S3": "T2", "S1": "T2"}}
    assert verdict(RUN, shuffled) == "same"
    assert verdict(RUN, {**RUN, "plan": {**RUN["plan"], "S4": "T1"}}) == "tie"


def test_a_run_that_stopped_early_is_never_the_same_run():
    assert verdict(RUN, {**RUN, "status": "FEASIBLE"}) == "different"
    assert verdict(RUN, dict(RUN)) == "same"
