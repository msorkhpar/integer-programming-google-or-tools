from iam_check import allowed

BUCKET = "arn:aws:s3:::trim-runs-example"
TRIM_JOB = {
    "Version": "2012-10-17",
    "Statement": [
        {"Effect": "Allow", "Action": ["s3:GetObject"], "Resource": [f"{BUCKET}/surveys/*"]},
        {"Effect": "Allow", "Action": "s3:PutObject", "Resource": f"{BUCKET}/trim-results/*"},
        {"Effect": "Deny", "Action": ["s3:*"], "Resource": [f"{BUCKET}/trim-results/locked/*"]},
    ],
}


def test_the_trim_job_reads_surveys_and_writes_results_only():
    assert allowed(TRIM_JOB, "s3:GetObject", f"{BUCKET}/surveys/sha256/ab.json") is True
    assert allowed(TRIM_JOB, "s3:PutObject", f"{BUCKET}/surveys/sha256/ab.json") is False
    assert allowed(TRIM_JOB, "s3:DeleteObject", f"{BUCKET}/trim-results/S-7/t-1.json") is False


def test_an_explicit_deny_wins_over_an_allow():
    assert allowed(TRIM_JOB, "s3:PutObject", f"{BUCKET}/trim-results/S-7/t-1.json") is True
    assert allowed(TRIM_JOB, "s3:PutObject", f"{BUCKET}/trim-results/locked/t-1.json") is False


def test_a_single_string_is_one_action_or_resource():
    assert allowed(TRIM_JOB, "s3:PutObject", f"{BUCKET}/trim-results/S-9/t-4.json") is True
    assert allowed(TRIM_JOB, "s", f"{BUCKET}/trim-results/S-9/t-4.json") is False


def test_actions_ignore_case_but_resources_do_not():
    assert allowed(TRIM_JOB, "S3:getobject", f"{BUCKET}/surveys/x.json") is True
    assert allowed(TRIM_JOB, "s3:GetObject", f"{BUCKET}/Surveys/x.json") is False


def test_a_question_mark_is_exactly_one_character():
    policy = {"Statement": [{"Effect": "Allow", "Action": "s3:GetObject", "Resource": f"{BUCKET}/S-?/*"}]}
    assert allowed(policy, "s3:GetObject", f"{BUCKET}/S-7/t-1.json") is True
    assert allowed(policy, "s3:GetObject", f"{BUCKET}/S-70/t-1.json") is False


def test_a_pattern_must_match_the_whole_name():
    policy = {"Statement": [{"Effect": "Allow", "Action": "s3:GetObject", "Resource": f"{BUCKET}/config.json"}]}
    assert allowed(policy, "s3:GetObject", f"{BUCKET}/config.json") is True
    assert allowed(policy, "s3:GetObject", f"{BUCKET}/config.json.bak") is False
    assert allowed(policy, "s3:GetObjectAcl", f"{BUCKET}/config.json") is False
