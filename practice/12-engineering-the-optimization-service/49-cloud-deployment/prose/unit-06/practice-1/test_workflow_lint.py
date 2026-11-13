import copy

from workflow_lint import lint

SHA = "1" * 40
CLEAN = {
    "name": "trim-ci",
    True: {"push": {"branches": ["main"]}},
    "permissions": {"contents": "read"},
    "jobs": {
        "test": {"runs-on": "ubuntu-24.04", "steps": [
            {"uses": f"actions/checkout@{SHA}"},
            {"run": "python -m pytest"}]},
        "push": {"needs": "test", "runs-on": "ubuntu-24.04",
                 "permissions": {"contents": "read", "id-token": "write"},
                 "steps": [
                     {"uses": f"aws-actions/configure-aws-credentials@{SHA}",
                      "with": {"role-to-assume": "arn:aws:iam::123456789012:role/trim-ci", "aws-region": "us-east-1"}},
                     {"run": "docker push example.invalid/trim:${{ github.sha }}"}]},
    },
}


def edited(change):
    flow = copy.deepcopy(CLEAN)
    change(flow)
    return flow


def test_a_clean_workflow_passes_and_a_careless_one_is_caught():
    assert lint(CLEAN) == []

    def careless(flow):
        del flow["permissions"]
        flow["jobs"]["test"]["steps"][0]["uses"] = "actions/checkout@v5"
        flow["jobs"]["push"]["steps"][0]["with"] = {"aws-access-key-id": "${{ secrets.AWS_KEY }}"}
    assert lint(edited(careless)) == ["push: uses secret AWS_KEY", "test: actions/checkout@v5 is not pinned to a commit SHA",
                                      "workflow: no top-level permissions"]


def test_a_short_sha_is_not_a_pin_and_a_local_action_needs_none():
    def change(flow):
        flow["jobs"]["test"]["steps"][0]["uses"] = "actions/checkout@1a2b3c4"
        flow["jobs"]["test"]["steps"].append({"uses": "./.github/actions/setup-trim"})
    assert lint(edited(change)) == ["test: actions/checkout@1a2b3c4 is not pinned to a commit SHA"]


def test_write_all_is_caught_at_both_levels():
    def change(flow):
        flow["permissions"] = "write-all"
        flow["jobs"]["test"]["permissions"] = "write-all"
    assert lint(edited(change)) == ["test: permissions write-all", "workflow: permissions write-all"]


def test_a_secret_in_a_run_line_is_found_and_github_token_is_allowed():
    def change(flow):
        flow["jobs"]["test"]["steps"].append({"run": "curl -H 'x: ${{ secrets.REPORT_TOKEN }}' example.invalid",
                                              "env": {"GH": "${{ secrets.GITHUB_TOKEN }}"}})
    assert lint(edited(change)) == ["test: uses secret REPORT_TOKEN"]


def test_id_token_write_needs_an_aws_credentials_step():
    def change(flow):
        flow["jobs"]["test"]["permissions"] = {"contents": "read", "id-token": "write"}
    assert lint(edited(change)) == ["test: id-token: write without an AWS credentials step"]


def test_a_workflow_level_id_token_is_inherited_by_a_job_without_its_own_permissions():
    def change(flow):
        flow["permissions"] = {"contents": "read", "id-token": "write"}
    assert lint(edited(change)) == ["test: id-token: write without an AWS credentials step"]
