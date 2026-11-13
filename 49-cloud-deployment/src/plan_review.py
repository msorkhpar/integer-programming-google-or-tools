"""Lesson 12.5.5: read a Terraform plan as JSON and stop the ones that would destroy stored runs.

The plan is deploy/terraform/sample-plan.json, written by hand in the documented shape of
`terraform show -json` (no Terraform runs in this course). GridCap is a fictional utility.
"""

import json
from pathlib import Path

PLAN = Path(__file__).resolve().parents[1] / "deploy" / "terraform" / "sample-plan.json"
#: What holds the service's history: losing one of these loses snapshots, results or images.
KEEPS_HISTORY = {"aws_s3_bucket", "aws_s3_bucket_versioning", "aws_ecr_repository"}


def verb(actions: list[str]) -> str:
    return {("no-op",): "no change", ("create",): "create", ("update",): "update in place",
            ("delete",): "destroy", ("delete", "create"): "replace (destroy first)",
            ("create", "delete"): "replace (create first)", ("read",): "read"}[tuple(actions)]


def blocked(change: dict) -> bool:
    return change["type"] in KEEPS_HISTORY and "delete" in change["change"]["actions"]


plan = json.loads(PLAN.read_text(encoding="utf-8"))
for change in plan["resource_changes"]:
    flag = "  <- blocked" if blocked(change) else ""
    print(f"{change['address']:<38} {verb(change['change']['actions'])}{flag}")
stops = [c["address"] for c in plan["resource_changes"] if blocked(c)]
print("apply allowed:", not stops, "| stopped by:", stops)
