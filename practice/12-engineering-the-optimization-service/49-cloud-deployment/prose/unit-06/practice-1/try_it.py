"""Run executes this file. Change the calls and see what prints. Submit grades."""
import logging

# Turn the logger up, so the `log.debug` lines of your code show under the printed lines.
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")
from workflow_lint import lint

SHA = "a" * 40
flow = {
    "name": "depot-ci",
    "permissions": {"contents": "read", "id-token": "write"},
    "jobs": {
        "check": {"runs-on": "ubuntu-24.04", "steps": [
            {"uses": "actions/setup-python@v6"},
            {"uses": "./.github/actions/prepare"},
            {"run": "echo ${{ secrets.GITHUB_TOKEN }} && make test"}]},
        "ship": {"runs-on": "ubuntu-24.04", "permissions": "write-all", "steps": [
            {"uses": f"actions/checkout@{SHA}"},
            {"run": "deploy", "env": {"TOKEN": "${{ secrets.DEPLOY_TOKEN }}"}}]},
    },
}

findings = lint(flow)
print("depot-ci findings:", len(findings))
for finding in findings:
    print("  ", finding)
