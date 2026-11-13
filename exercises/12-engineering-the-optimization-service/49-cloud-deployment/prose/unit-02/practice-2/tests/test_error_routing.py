from error_routing import route

PUBLISH = {
    "Type": "Task",
    "Retry": [
        {"ErrorEquals": ["Report.Throttled", "Report.Busy"], "MaxAttempts": 2},
        {"ErrorEquals": ["Report.Timeout"]},
    ],
    "Catch": [
        {"ErrorEquals": ["Report.BadInput"], "Next": "RejectScenario"},
        {"ErrorEquals": ["States.ALL"], "Next": "AlertOperators"},
    ],
}


def test_retries_then_success_and_a_caught_error():
    assert route(PUBLISH, ["Report.Throttled"]) == ["retry", "succeeded"]
    assert route(PUBLISH, ["Report.BadInput"]) == ["catch:RejectScenario"]


def test_a_retrier_stops_at_its_max_attempts():
    assert route(PUBLISH, ["Report.Busy", "Report.Throttled", "Report.Busy"]) == ["retry", "retry", "catch:AlertOperators"]


def test_max_attempts_defaults_to_three():
    assert route(PUBLISH, ["Report.Timeout"] * 4) == ["retry", "retry", "retry", "catch:AlertOperators"]


def test_each_retrier_counts_its_own_attempts():
    errors = ["Report.Throttled", "Report.Timeout", "Report.Throttled", "Report.Timeout"]
    assert route(PUBLISH, errors) == ["retry", "retry", "retry", "retry", "succeeded"]


def test_an_exhausted_retrier_does_not_fall_through_to_a_later_one():
    state = {"Retry": [{"ErrorEquals": ["Report.Busy"], "MaxAttempts": 1},
                       {"ErrorEquals": ["States.ALL"], "MaxAttempts": 5}],
             "Catch": [{"ErrorEquals": ["States.ALL"], "Next": "AlertOperators"}]}
    assert route(state, ["Report.Busy", "Report.Busy"]) == ["retry", "catch:AlertOperators"]


def test_task_failed_matches_everything_but_a_timeout():
    state = {"Catch": [{"ErrorEquals": ["States.TaskFailed"], "Next": "RecordFailure"}]}
    assert route(state, ["Report.Busy"]) == ["catch:RecordFailure"]
    assert route(state, ["States.Timeout"]) == ["fail"]


def test_max_attempts_zero_never_retries():
    state = {"Retry": [{"ErrorEquals": ["States.Timeout"], "MaxAttempts": 0}],
             "Catch": [{"ErrorEquals": ["States.Timeout"], "Next": "RecordFailure"}]}
    assert route(state, ["States.Timeout"]) == ["catch:RecordFailure"]
