from audit import audit

# A water utility's stored runs. Not the lesson's.
RUN = {"snapshot": "9a1c", "settings": {"threads": 1, "seed": 7}, "status": "OPTIMAL", "objective": 812.0,
       "plan": {"W1": 2027, "W3": 2028, "W5": 2029}}


def test_an_identical_replay_has_no_findings():
    assert audit(RUN, {**RUN, "plan": dict(RUN["plan"]), "settings": dict(RUN["settings"])}) == []


def test_each_difference_is_reported_in_order():
    replay = {**RUN, "settings": {"threads": 8, "seed": 7}, "objective": 790.0,
              "plan": {"W1": 2027, "W3": 2029, "W5": 2029}}
    assert audit(RUN, replay) == ["settings differ: threads", "objective differs", "plan differs: W3"]
    assert audit(RUN, {**RUN, "status": "FEASIBLE"}) == ["status differs"]


def test_a_replay_on_other_inputs_proves_nothing():
    replay = {**RUN, "snapshot": "77b0", "objective": 700.0, "plan": {"W1": 2028}}
    assert audit(RUN, replay) == ["inputs differ"]


def test_rounding_noise_in_the_objective_is_not_a_finding():
    assert audit(RUN, {**RUN, "objective": 812.0000001}) == []
    assert audit(RUN, {**RUN, "objective": 812.01}) == ["objective differs"]


def test_a_project_in_only_one_plan_is_a_difference():
    replay = {**RUN, "plan": {"W1": 2027, "W3": 2028, "W6": 2029}}
    assert audit(RUN, replay) == ["plan differs: W5, W6"]
