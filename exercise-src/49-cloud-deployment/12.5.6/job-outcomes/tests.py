from job_outcomes import outcomes

TRIM = {
    "test": {},
    "image": {"needs": "test", "if": "github.event_name == 'push'"},
    "deploy": {"needs": ["test", "image"], "if": "github.event_name == 'push'"},
}


def test_a_push_runs_everything_and_a_pull_request_skips_the_deploy_chain():
    assert outcomes(TRIM, "push", failing={"deploy"}) == {"test": "success", "image": "success", "deploy": "failure"}
    assert outcomes(TRIM, "pull_request") == {"test": "success", "image": "skipped", "deploy": "skipped"}


def test_a_failure_skips_every_job_down_the_chain():
    jobs = {"test": {}, "build": {"needs": "test"}, "deploy": {"needs": "build"}}
    assert outcomes(jobs, "push", failing={"test"}) == {"test": "failure", "build": "skipped", "deploy": "skipped"}


def test_a_skipped_need_skips_the_job_too():
    jobs = {"a": {"if": "github.event_name == 'push'"}, "b": {"needs": "a"}}
    assert outcomes(jobs, "pull_request") == {"a": "skipped", "b": "skipped"}


def test_always_runs_after_a_failed_need():
    jobs = {"a": {}, "notify": {"needs": "a", "if": "always()"}}
    assert outcomes(jobs, "push", failing={"a"}) == {"a": "failure", "notify": "success"}


def test_jobs_may_be_listed_before_the_jobs_they_need():
    jobs = {"deploy": {"needs": ["build"]}, "build": {"needs": "test"}, "test": {}}
    assert outcomes(jobs, "push", failing={"test"}) == {"test": "failure", "build": "skipped", "deploy": "skipped"}


def test_a_job_with_several_needs_waits_for_all_of_them():
    jobs = {"unit": {}, "lint": {}, "image": {"needs": ["unit", "lint"]}}
    assert outcomes(jobs, "push", failing={"lint"}) == {"unit": "success", "lint": "failure", "image": "skipped"}


def test_always_does_not_override_the_event_test():
    jobs = {"a": {}, "notify": {"needs": "a", "if": "always() && github.event_name == 'push'"}}
    assert outcomes(jobs, "pull_request", failing={"a"}) == {"a": "failure", "notify": "skipped"}
    assert outcomes(jobs, "push", failing={"a"}) == {"a": "failure", "notify": "success"}
