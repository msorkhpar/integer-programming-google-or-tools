from submit_check import problems

GOOD = {
    "jobName": "run-0042",
    "jobQueue": "gridcap-solves",
    "jobDefinition": "gridcap-solve",
    "containerOverrides": {
        "environment": [{"name": "RUN_ID", "value": "run-0042"}, {"name": "TIME_LIMIT_S", "value": "60"}],
        "resourceRequirements": [{"type": "VCPU", "value": "2"}, {"type": "MEMORY", "value": "8192"}],
    },
    "timeout": {"attemptDurationSeconds": 660},
    "retryStrategy": {"attempts": 2},
}


def with_(**changes):
    return {**GOOD, **changes}


def sized(vcpu, memory):
    return with_(containerOverrides={**GOOD["containerOverrides"], "resourceRequirements": [
        {"type": "VCPU", "value": vcpu}, {"type": "MEMORY", "value": memory}]})


def test_a_good_request_passes_and_a_bad_one_lists_every_problem():
    assert problems(GOOD) == []
    bad = with_(jobName="run 42!", timeout={"attemptDurationSeconds": 30}, retryStrategy={"attempts": 0})
    assert problems(bad) == ["jobName 'run 42!' is not a valid job name", "timeout 30 s is under 60 s",
                             "retry attempts 0 is outside 1-10"]


def test_the_name_starts_with_a_letter_or_digit_and_has_at_most_128_characters():
    assert problems(with_(jobName="_run-42")) == ["jobName '_run-42' is not a valid job name"]
    assert problems(with_(jobName="r" * 128)) == []
    assert problems(with_(jobName="r" * 129)) == [f"jobName '{'r' * 129}' is not a valid job name"]


def test_60_seconds_and_10_attempts_are_allowed():
    assert problems(with_(timeout={"attemptDurationSeconds": 60}, retryStrategy={"attempts": 10})) == []
    assert problems(with_(retryStrategy={"attempts": 11})) == ["retry attempts 11 is outside 1-10"]


def test_a_size_must_be_a_fargate_pair():
    assert problems(sized("1", "3072")) == []
    assert problems(sized("0.5", "4096")) == []
    assert problems(sized("1", "12288")) == ["VCPU 1 with MEMORY 12288 is not a Fargate size"]
    assert problems(sized("8", "18432")) == ["VCPU 8 with MEMORY 18432 is not a Fargate size"]


def test_vcpu_without_memory_is_refused():
    one = with_(containerOverrides={"resourceRequirements": [{"type": "VCPU", "value": "4"}]})
    assert problems(one) == ["VCPU and MEMORY must be given together"]


def test_a_variable_set_twice_is_refused():
    env = GOOD["containerOverrides"]["environment"] + [{"name": "RUN_ID", "value": "run-0043"}]
    twice = with_(containerOverrides={**GOOD["containerOverrides"], "environment": env})
    assert problems(twice) == ["environment variable RUN_ID is set twice"]
